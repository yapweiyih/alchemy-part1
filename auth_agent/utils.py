import logging
import os
import subprocess

from dotenv import load_dotenv
from google.adk.agents.callback_context import CallbackContext

from .util_auth import get_valid_token

load_dotenv()

logger = logging.getLogger(__name__)
AUTH_ID = os.getenv("AUTH_ID", None)


def get_adk_agent_token(callback_context) -> str:
    # Either use Agentspace token or Dev custom token from .env
    # Use env variable file
    print()
    print("************** get_adk_agent_token (START) **************")
    access_token = os.getenv("ACCESS_TOKEN")
    if access_token:
        print("Use .env access token.")
    else:
        if os.getenv("DEBUG") == "0":
            print("Use Agentspace access token.")
            access_token = get_agentspace_access_token(callback_context)
        else:
            print("Use debug access token.")
            access_token = get_valid_token()

    # if not access_token:
    #     raise ValueError("No access token found. Please check your authentication.")

    print(f"Access Token: {access_token}")  # type: ignore

    # user_info = extract_user_info(access_token)  # type: ignore
    # print(f"user_info: {user_info}")

    print("************** get_adk_agent_token (END) **************")
    print()
    return access_token  # type: ignore


def get_development_access_token():
    access_token = None
    try:
        # Execute the gcloud command to get the access token
        access_token_process = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            check=True,
        )
        access_token = access_token_process.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.info(f"Error getting gcloud access token: {e}")
        logger.info(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        logger.info(
            "Error: 'gcloud' command not found. Please ensure Google Cloud SDK is installed and configured."
        )
    finally:
        return access_token


def get_agentspace_access_token(tool_context: CallbackContext) -> str | None:
    """Retrieve the access token from the tool context."""
    auth_id = AUTH_ID
    if f"{auth_id}" in tool_context.state:
        token = tool_context.state[f"{auth_id}"]
        logger.info(f"Found agentspace token: {token}")
        if isinstance(token, str):
            return token
        elif isinstance(token, dict) and "access_token" in token:
            return token["access_token"]
    return None
