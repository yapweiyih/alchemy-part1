########################################################
# UPDATE CONFIGURATION HERE
########################################################

export PROJECT_NUMBER="671247654914"
export LOCATION="us-central1"
export APP_ID="agentspace-dev_1744685873939"
export DESCRIPTION="You are a helpful assistant."
export TOOL_DESCRIPTION="You are a helpful assistant."
export DISPLAY_NAME=auth-agent-v10
export OLD_AGENT_ID=14226993668844730339
export ADK_DEPLOYMENT_ID=505062865242161152


# Get AUTH_ID from Google Secret Manager
export AUTH_ID=$(gcloud secrets versions access latest --secret="AGENTSPACE_WEB_AUTH_ID" --project="$PROJECT_NUMBER")

# Copy and paste from notebook step 1.
export OAUTH_AUTH_URI="https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=671247654914-onsqf0obdfnkdpr0uj59hruev41u54i1.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Foauth-redirect&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.modify&state=aQhsWAu8rLfQKqzSicWgYsB7OR8zLC&access_type=online&include_granted_scopes=true&prompt=consent"

# Get OAuth configuration from Google Secret Manager
export OAUTH_SECRET_JSON=$(gcloud secrets versions access latest --secret="AGENTSPACE_WEB_SECRET_JSON" --project="$PROJECT_NUMBER") # pragma: allowlist secret
export OAUTH_CLIENT_ID=$(echo "$OAUTH_SECRET_JSON" | jq -r '.web.client_id')
export OAUTH_CLIENT_SECRET=$(echo "$OAUTH_SECRET_JSON" | jq -r '.web.client_secret')
export OAUTH_TOKEN_URI=$(echo "$OAUTH_SECRET_JSON" | jq -r '.web.token_uri')
