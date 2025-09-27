import base64
import logging
import os
from typing import Any, Dict

import requests
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.function_tool import ToolContext
from google.cloud import secretmanager
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

load_dotenv()

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
AUTH_ID = os.getenv(
    "AGENTSPACE_AUTH_ID"
)  # This is set in .env file (local dev), or in ae_deploy.py (agent engine deployment)
print(f"PROJECT_ID: {project_id}")
print(f"AUTH_ID: {AUTH_ID}")


def extract_user_info(access_token: str) -> Dict[str, Any]:
    """
    Extract user information from Google OAuth access token using Google's OAuth2 API.
    """

    try:
        url = f"https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={access_token}"
        response = requests.get(url)

        if response.status_code == 200:
            token_info = response.json()
            print(f"Token info from Google API: {token_info}")
            return {
                "status": "authenticated",
                "user_info": token_info,
            }
        else:
            return {
                "status": "error",
                "message": "Failed to get token info from Google API: {response.status_code} - {response.text}",
            }

    except Exception as e:
        logger.error(f"Error extracting user info from Google API: {e}")
        return {
            "status": "error",
            "message": f"Error: {e}",
        }


def get_access_token(tool_context: ToolContext) -> str | None:
    """Retrieve the access token from the tool context."""
    if f"temp:{AUTH_ID}" in tool_context.state:
        token = tool_context.state[f"temp:{AUTH_ID}"]
        if isinstance(token, str):
            return token
        elif isinstance(token, dict) and "access_token" in token:
            return token["access_token"]
    return None


def check_auth(tool_context: ToolContext):
    """
    Check if the user is authenticated by verifying the presence and validity of the access token
    in the tool context's state. If authenticated, retrieves and stores user information from Google OAuth.

    Args:
        tool_context (ToolContext): The context containing session state and temporary tokens.

    Returns:
        dict: A dictionary indicating authentication status and user information or error message.
    """

    try:
        access_token = get_access_token(tool_context)
        if not access_token:
            return {
                "status": "not_authenticated",
                "message": "No valid access token found",
            }

        print(
            f"Access token: {access_token[:20]}..."
        )  # Log only first 20 chars for security

        user_info = extract_user_info(access_token)
        if user_info:
            # Store both the token and user info
            tool_context.state[f"temp:{AUTH_ID}"] = {
                "access_token": access_token,
                "user_info": user_info,
            }

        tool_context.state["user_info"] = user_info
        print(f"check_auth state after: {tool_context.state.to_dict()}")
        return {
            "status": "authenticated",
            "user_info": user_info,
        }

    except Exception as e:
        logger.error(f"Error checking auth: {e}")
        return {
            "status": "error",
            "message": str(e),
        }


def send_email(
    to: str,
    subject: str,
    body: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Send an email using Gmail API with the authenticated user's access token.

    Example:
        send_email(
            to='joedoe@gmail.com',
            subject='Hello',
            body='Hello, how are you?'
        )

    Args:
        to (str): the email address to send the email to.
        subject (str): The subject of the email.
        body (str): The body of the email.
        tool_context (ToolContext): The tool context containing the access token.

    Returns:
        Dict[str, Any]: The result of the email sending operation.
    """

    # Check if user is authenticated
    print(f"send_email, to: {to}, subject: {subject}, body: {body}")
    access_token = get_access_token(tool_context)
    if not access_token:
        return {
            "error": "User not authenticated",
            "message": "Please authenticate first using check_auth",
        }

    try:
        # Create credentials object from access token
        credentials = Credentials(
            token=access_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=None,  # Not needed for access token usage
            client_secret=None,  # Not needed for access token usage
            scopes=["https://www.googleapis.com/auth/gmail.send"],
        )

        # Build Gmail service
        service = build("gmail", "v1", credentials=credentials)

        # Create the email message
        message = {
            "raw": base64.urlsafe_b64encode(
                f"To: {to}\r\nSubject: {subject}\r\n\r\n{body}".encode("utf-8")
            ).decode("utf-8")
        }

        # Send the email
        messages_result = (
            service.users().messages().send(userId="me", body=message).execute()
        )

        print(f"Email sent successfully: {messages_result}")

        return {
            "success": True,
            "message_id": messages_result.get("id"),
            "thread_id": messages_result.get("threadId"),
            "message": "Email sent successfully",
        }

    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return {"error": str(e), "message": "Failed to send email"}


async def before_agent_callback(callback_context: CallbackContext):
    callback_context.state[f"temp:{AUTH_ID}"] = "xxx"
    print(f"before_agent_callback state: {callback_context.state.to_dict()}")
    return None


root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="root_agent",
    instruction="""You are a helpful assistant that can help with authentication and sending emails.

    1. If the user says check_auth:
       1.1 call check_auth to retrieve the following information:
          - Username
          - Email
          - Access Scope/Permissions

    2. If the user says send_email:
       2.1 Ask for the recipient's email address, subject, and body of the email.
       2.2 Send emails through Gmail API with send_email.

    3. Do not answer any other questions. Politely inform the user that you can only assist with authentication and sending emails.

    """,
    tools=[check_auth, send_email],
    # before_agent_callback=before_agent_callback,
)
