import json
import logging
import os
import secrets
import threading
import time
import urllib.parse
import webbrowser
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
from dotenv import load_dotenv
from google.cloud import secretmanager

load_dotenv()

logger = logging.getLogger(__name__)
sm_client = secretmanager.SecretManagerServiceClient()


def get_secret(secret_id, project_id):
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = sm_client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


# ServiceNow OAuth Configuration
SERVICENOW_INSTANCE = os.getenv("SERVICENOW_INSTANCE")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
client_id = get_secret("AUSPOST_CLIENT_ID", PROJECT_ID)
client_secret = get_secret("AUSPOST_CLIENT_SECRET", PROJECT_ID)

# ServiceNow OAuth endpoints
auth_url = f"https://{SERVICENOW_INSTANCE}/oauth_auth.do"
token_url = f"https://{SERVICENOW_INSTANCE}/oauth_token.do"
redirect_uri = "http://localhost:8080/callback"

scopes = ["useraccount"]
logger.debug(f"client_id: {client_id}")
logger.debug(f"client_secret: {client_secret}")
logger.debug(f"auth_url: {auth_url}")
logger.debug(f"token_url: {token_url}")
logger.debug(f"redirect_uri: {redirect_uri}")


# Global variables to store the authorization code and state
auth_code = None
oauth_state = None


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code, oauth_state
        if self.path.startswith("/callback"):
            # Parse the authorization code from the callback URL
            query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

            # Validate state parameter to prevent CSRF attacks
            if "state" in query_params:
                received_state = query_params["state"][0]
                if received_state != oauth_state:
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(
                        b"<html><body><h1>Authorization failed!</h1><p>Invalid state parameter (CSRF protection).</p></body></html>"
                    )
                    return

            if "code" in query_params:
                auth_code = query_params["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h1>Authorization successful!</h1><p>You can close this window.</p></body></html>"
                )
            else:
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h1>Authorization failed!</h1></body></html>"
                )
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress log messages
        pass


def get_authorization_code():
    """Start a local server and get authorization code from user"""
    global auth_code, oauth_state

    # Generate a random state parameter for CSRF protection
    oauth_state = secrets.token_urlsafe(32)

    # Start local server
    server = HTTPServer(("localhost", 8080), CallbackHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # Build ServiceNow OAuth authorization URL with state parameter
    auth_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
        "state": oauth_state,
    }

    # Construct the authorization URL with proper encoding
    authorization_url = f"{auth_url}?{urllib.parse.urlencode(auth_params)}"

    print("Opening browser for ServiceNow authorization...")
    print(f"If browser doesn't open, visit: {authorization_url}")
    webbrowser.open(authorization_url)

    # Wait for authorization code
    print("Waiting for authorization...")
    timeout = 60  # 60 seconds timeout, click refresh if needed.
    start_time = time.time()

    while auth_code is None and (time.time() - start_time) < timeout:
        time.sleep(0.5)

    server.shutdown()

    if auth_code is None:
        raise Exception("Authorization timed out or failed")

    return auth_code


def exchange_code_for_token(code):
    """Exchange authorization code for access token"""
    token_data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "code": code,
    }

    response = requests.post(token_url, data=token_data)
    response.raise_for_status()

    token_info = response.json()
    # Add expiration time
    if "expires_in" in token_info:
        # Calculate expiration time and add it to token_info
        expires_in = token_info["expires_in"]
        expiration_time = datetime.now() + timedelta(seconds=expires_in)
        token_info["expiration_time"] = expiration_time.isoformat()

    return token_info


def refresh_access_token(refresh_token):
    """Refresh the access token using the refresh token"""
    token_data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }

    response = requests.post(token_url, data=token_data)
    response.raise_for_status()

    token_info = response.json()
    # Add expiration time
    if "expires_in" in token_info:
        # Calculate expiration time and add it to token_info
        expires_in = token_info["expires_in"]
        expiration_time = datetime.now() + timedelta(seconds=expires_in)
        token_info["expiration_time"] = expiration_time.isoformat()

    print(token_info["expiration_time"])
    return token_info


def is_token_expired(token_info):
    """Check if the token is expired"""
    if "expiration_time" not in token_info:
        # If no expiration time, assume it's expired to be safe
        return True

    expiration_time = datetime.fromisoformat(token_info["expiration_time"])
    print(f"Current date/time: {datetime.now()}")
    print(f"Expiry date/time: {expiration_time}")
    # Add a buffer of 5 minutes to refresh before actual expiration
    buffer_time = timedelta(minutes=5)

    return datetime.now() > (expiration_time - buffer_time)


def save_token_info(token_info, file_path="token_info.json"):
    """Save token information to a file"""
    with open(file_path, "w") as f:
        json.dump(token_info, f)


def load_token_info(file_path="token_info.json"):
    """Load token information from a file"""
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r") as f:
        return json.load(f)


def get_valid_token():
    """Get a valid access token, refreshing if necessary"""

    token_info = load_token_info()

    if token_info is None:
        print("Token.json not found...")
        code = get_authorization_code()
        token_info = exchange_code_for_token(code)
        save_token_info(token_info)
    elif is_token_expired(token_info):
        print("Access token expired, refreshing...")
        if "refresh_token" in token_info:
            try:
                token_info = refresh_access_token(token_info["refresh_token"])
                save_token_info(token_info)
            except requests.exceptions.HTTPError as e:
                # If refresh fails (400 Bad Request), the refresh token is invalid
                print(f"Refresh token is invalid or expired: {e}")
                print("Getting a new token...")
                code = get_authorization_code()
                token_info = exchange_code_for_token(code)
                save_token_info(token_info)
        else:
            print("No refresh token found.")
            print("Getting a new token...")
            code = get_authorization_code()
            token_info = exchange_code_for_token(code)
            save_token_info(token_info)
    else:
        print("token.json is valid...")

    return token_info["access_token"]


if __name__ == "__main__":

    pass
