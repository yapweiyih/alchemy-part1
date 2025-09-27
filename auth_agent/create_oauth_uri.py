import json
import os
import subprocess

import google_auth_oauthlib.flow
from dotenv import load_dotenv
from google.cloud import secretmanager

load_dotenv()
client = secretmanager.SecretManagerServiceClient()


def get_secret(secret_id, project_id):
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
CLIENT_JSON = get_secret("AGENTSPACE_WEB_SECRET_JSON", PROJECT_ID)

result = subprocess.run(
    ["gcloud", "projects", "describe", PROJECT_ID, "--format=value(projectNumber)"],
    capture_output=True,
    text=True,
    check=True,
)
PROJECT_NUMBER = result.stdout.strip()

print(f"PROJECT_ID: {PROJECT_ID}")
print(f"PROJECT_NUMBER: {PROJECT_NUMBER}")

client_config = json.loads(CLIENT_JSON)

# Scope: https://developers.google.com/identity/protocols/oauth2/scopes
flow = google_auth_oauthlib.flow.Flow.from_client_config(
    client_config,
    scopes=[
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.labels",
    ],
)

flow.redirect_uri = "https://vertexaisearch.cloud.google.com/oauth-redirect"

authorization_url, state = flow.authorization_url(
    access_type="online",  # Recommended, enable offline access so that you can refresh an access token without re-prompting
    include_granted_scopes="true",
    prompt="consent",
)

# Append to .env file
with open(".env", "a") as f:
    f.write(f'OAUTH_AUTH_URI="{authorization_url}"')


print("*" * 20)
print("OAUTH_AUTH_URI:")
print(authorization_url)
print("*" * 20)
