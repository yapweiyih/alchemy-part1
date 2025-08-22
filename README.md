# Agentspace Auth

## Prerequisites
- Create agentspace `Client ID` and `Client SECRET` using GCP Auth Platform for `Web Application` type.

- Copy and paste to store the content of the client secret JSON in Google Secret Manager as `AGENTSPACE_WEB_SECRET_JSON`.

- Make sure Reasoning Engine service account has permission `secretmanager.versions.access`.

- Store agentspace `AUTH_ID` in Google Secret Manager as `AGENTSPACE_WEB_AUTH_ID`

- Next create OAuth Auth URL and agentspace AUTH_ID with the correct scopes using `agent_registration.ipynb` in Step 1 and 2.

## Deploy

- Update `ae_deploy.py` with the correct configuration values.
    ```python
    PROJECT_ID = "hello-world-418507"
    LOCATION = "us-central1"
    DISPLAY_NAME = "auth-agent-20250727"
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
    ```
- Deploy ADK agent to Agent Engine using `uv run ae_deploy.py`
- Once it is done, you will get a Reasoning Engine id.

## Register with Agentspace

- Update `configuration.sh` configuration, then run the script.
    ```bash
    export PROJECT_NUMBER="671247654914"
    export LOCATION="us-central1"
    export APP_ID="agentspace-dev_1744685873939"
    export DESCRIPTION="You are a helpful assistant."
    export TOOL_DESCRIPTION="You are a helpful assistant."
    export DISPLAY_NAME=auth-agent
    export OLD_AGENT_ID=111
    export ADK_DEPLOYMENT_ID=205573490022023168 # Reasoning engine id
    ```

- Register ADK on Agent Engine to Agentspace using the command below
```bash
bash run_register_auth.sh
```

- Now you should be able to see your custom ADK agent on Agentspace.


## Agentspace Test
- When you open the auth agent, you need to login to your personal email to test
- Authenticate with your personal email.
- Enter "get user info"
- Enter "send email to abc@gmail.com with subject:test, body: harlo"
