import asyncio
import json
import logging
import os
import sys
import time

import vertexai
from google.cloud import secretmanager


def get_secret(secret_id, project_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


########################################################
# Change the following variables to match your project
########################################################
PROJECT_ID = "hello-world-418507"
LOCATION = "us-central1"
DISPLAY_NAME = "auth-agent-v10"
STAGING_BUCKET = "gs://2025-adk-workshop"
AUTH_ID = get_secret("AGENTSPACE_WEB_AUTH_ID", PROJECT_ID)
print(f"AUTH_ID: {AUTH_ID}")

EXTRA_PACKAGES = ["./auth_agent"]
REQUIREMENTS = [
    "db-dtypes>=1.4.3",
    "google-adk>=1.7.0",
    "google-auth-oauthlib>=1.2.2",
    "google-cloud-aiplatform>=1.105.0",
    "google-cloud-bigquery-connection>=1.18.3",
    "google-cloud-bigquery-storage>=2.32.0",
    "google-genai>=1.27.0",
    "ipykernel>=6.29.5",
    "pandas>=2.3.0",
    "tabulate>=0.9.0",
    "PyJWT>=2.8.0",
]
ENV_VARS = {
    "GOOGLE_GENAI_USE_VERTEXAI": "TRUE",
    "AGENTSPACE_AUTH_ID": AUTH_ID,
}

########################################################

logging.getLogger("google").setLevel(logging.ERROR)

# Step descriptions
STEPS = [
    "Set environment variables and logging",
    "Initialize Vertex AI",
    "Local test (async)",
    "Deploy agent to Vertex AI",
    "Test deployed agent on cloud (sync)",
]


def step_progress(step_idx):
    print(f"\n[Step {step_idx + 1}/{len(STEPS)}] {STEPS[step_idx]}")
    print()


# Timing decorator for steps
def timed_step(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"\n--- Step runtime: {end - start:.2f} seconds ---\n")
        return result

    return wrapper


def set_env_and_logging():
    step_progress(0)
    os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
    os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"  # Use Vertex AI API
    os.environ["AGENTSPACE_AUTH_ID"] = AUTH_ID
    print("Environment variables set.")


def init_vertexai():
    step_progress(1)
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )
    print("Vertex AI initialized.")


def import_agent():
    from vertexai.preview import reasoning_engines

    from auth_agent.agent import root_agent

    return reasoning_engines, root_agent


@timed_step
async def local_test():
    step_progress(2)
    reasoning_engines, root_agent = import_agent()
    app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )
    session = await app.async_create_session(user_id="u_123")
    PROMPT = "hi?"
    print("Local test session created.")
    async for event in app.async_stream_query(
        user_id="u_123",
        session_id=session.id,
        message=PROMPT,
    ):
        print("*" * 40)
        content = event.get("content", {})
        parts = content.get("parts", [])

        for part in parts:
            if "thought_signature" in part:
                print(f"Thought Signature: {part['thought_signature']}")

            if "function_call" in part:
                func_call = part["function_call"]
                print(f"Function Call - Name: {func_call.get('name')}")
                print(f"Function Call - Args: {func_call.get('args')}")

            if "function_response" in part:
                func_response = part["function_response"]
                print(f"Function Response - Name: {func_response.get('name')}")
                print(f"Function Response - Result: {func_response.get('response')}")

            if "text" in part:
                print(f"Text: {part['text']}")
    print("Local test completed.")


@timed_step
def deploy_agent():
    step_progress(3)
    from vertexai import agent_engines

    _, root_agent = import_agent()
    remote_app = agent_engines.create(
        display_name=DISPLAY_NAME,
        agent_engine=root_agent,
        requirements=REQUIREMENTS,
        extra_packages=EXTRA_PACKAGES,
        env_vars=ENV_VARS,
    )
    ENGINE_ID = remote_app.resource_name.split("/")[-1]
    print(f"Agent deployed. ENGINE_ID: {ENGINE_ID}")
    return ENGINE_ID


@timed_step
def test_on_cloud(engine_id):
    step_progress(4)
    live_app = vertexai.agent_engines.get(
        f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{engine_id}"
    )
    session = live_app.create_session(user_id="u_123")
    print(f"Cloud test session created: {session}")
    for PROMPT in ["hi?"]:
        request_json = json.dumps(
            {
                "user_id": "u_123",
                "session_id": session["id"],
                "message": {
                    "parts": [{"text": PROMPT}],
                    "role": "user",
                },
            }
        )
        events = list(
            live_app.streaming_agent_run_with_events(request_json=request_json)
        )
        print(f"\nPrompt: {PROMPT}")
        for event_group in events:
            for event in event_group.get("events", []):
                content = event.get("content", {})
                parts = content.get("parts", [])
                for part in parts:
                    if "function_call" in part:
                        func_call = part["function_call"]
                        print(f"function_call - Name: {func_call.get('name')}")
                    elif "function_response" in part:
                        func_response = part["function_response"]
                        print(f"function_response - Name: {func_response.get('name')}")
                    elif "text" in part:
                        print(f"Text: {part['text']}")
    print("Cloud test completed.")


def main():
    try:
        set_env_and_logging()
        init_vertexai()
        asyncio.run(local_test())
        engine_id = deploy_agent()
        test_on_cloud(engine_id)
        print(f"\nAll {len(STEPS)}/{len(STEPS)} steps completed successfully.")
    except Exception as e:
        print(f"\nError: {e}")
        print("Aborting further steps.")
        sys.exit(1)


if __name__ == "__main__":
    main()
