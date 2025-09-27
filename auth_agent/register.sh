#! /bin/env bash

########################################################
# UPDATE CONFIGURATION HERE
########################################################
# Get project number from GOOGLE_CLOUD_PROJECT environment variable

GOOGLE_CLOUD_PROJECT="hello-world-418507"
APP_ID="agentspace-dev_1744685873939" # This is the agentspace engine id
OAUTH_AUTH_URI="https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=671247654914-onsqf0obdfnkdpr0uj59hruev41u54i1.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Foauth-redirect&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive.readonly+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive.metadata.readonly+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.readonly+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar.readonly&state=yqeQwcuX7kfIlExgKePq8Rhzj1ZpIi&access_type=offline&include_granted_scopes=true&login_hint=hint%40example.com&prompt=consent"

########################################################

if [ -n "$GOOGLE_CLOUD_PROJECT" ]; then
  PROJECT_NUMBER=$(gcloud projects describe "$GOOGLE_CLOUD_PROJECT" --format="value(projectNumber)")
else
  echo "Error: GOOGLE_CLOUD_PROJECT environment variable is not set"
  exit 1
fi

DESCRIPTION="This is your AI productivity agent"
TOOL_DESCRIPTION="You are a AI productivity agent."
LOCATION="us-central1"
OAUTH_CLIENT_ID=$(gcloud secrets versions access latest --secret="AGENTSPACE_WEB_CLIENTID" --project="${PROJECT_NUMBER}")
OAUTH_CLIENT_SECRET=$(gcloud secrets versions access latest --secret="AGENTSPACE_WEB_CLIENTSECRET" --project="${PROJECT_NUMBER}") # pragma: allowlist secret
OAUTH_TOKEN_URI="https://oauth2.googleapis.com/token"


usage() {
  echo "Usage: $0 {"
  echo "  register <ADK_DEPLOYMENT_ID> <DISPLAY_NAME> |"
  echo "  list [name] |"
  echo "  delete <AGENT_ID> |"
  echo "  register-auth <ADK_DEPLOYMENT_ID> <AUTH_ID> <DISPLAY_NAME> |"
  echo "  update <AGENT_ID> <ADK_DEPLOYMENT_ID> <DISPLAY_NAME> |"
  echo "  update-auth <AGENT_ID> <ADK_DEPLOYMENT_ID> <AUTH_ID> <DISPLAY_NAME>"
  echo "}"
  exit 1
}

if [ $# -lt 1 ]; then
  usage
fi

COMMAND=$1

case $COMMAND in
  register)
    if [ $# -ne 3 ]; then
      echo "Error: register requires ADK_DEPLOYMENT_ID and DISPLAY_NAME arguments."
      usage
    fi
    ADK_DEPLOYMENT_ID=$2
    DISPLAY_NAME=$3
    curl -X POST \
      -H "Authorization: Bearer $(gcloud auth print-access-token)" \
      -H "Content-Type: application/json" \
      -H "X-Goog-User-Project: ${PROJECT_NUMBER}" \
      "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents" \
      -d '{
        "displayName": "'"${DISPLAY_NAME}"'",
        "description": "'"${DESCRIPTION}"'",
        "adk_agent_definition": {
          "tool_settings": {
            "tool_description": "'"${TOOL_DESCRIPTION}"'"
          },
          "provisioned_reasoning_engine": {
            "reasoning_engine": "projects/'"${PROJECT_NUMBER}"'/locations/'"${LOCATION}"'/reasoningEngines/'"${ADK_DEPLOYMENT_ID}"'"
          }
        }
      }'
    ;;
  register-auth)
    if [ $# -ne 4 ]; then
      echo "Error: register-auth requires ADK_DEPLOYMENT_ID, AUTH_ID, and DISPLAY_NAME arguments."
      usage
    fi
    ADK_DEPLOYMENT_ID=$2
    AUTH_ID=$3
    DISPLAY_NAME=$4

    curl -X POST \
      -H "Authorization: Bearer $(gcloud auth print-access-token)" \
      -H "Content-Type: application/json" \
      -H "X-Goog-User-Project: ${PROJECT_NUMBER}" \
      "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents" \
      -d '{
        "displayName": "'"${DISPLAY_NAME}"'",
        "description": "'"${DESCRIPTION}"'",
        "adk_agent_definition": {
          "tool_settings": {
            "tool_description": "'"${TOOL_DESCRIPTION}"'"
          },
          "provisioned_reasoning_engine": {
            "reasoning_engine": "projects/'"${PROJECT_NUMBER}"'/locations/'"${LOCATION}"'/reasoningEngines/'"${ADK_DEPLOYMENT_ID}"'"
          },
          "authorizations": [
            "projects/'"${PROJECT_NUMBER}"'/locations/global/authorizations/'"${AUTH_ID}"'"
          ]
        }
      }'
    ;;
  create-auth)
    if [ $# -ne 2 ]; then
      echo "Error: create-auth requires AUTH_ID argument."
      usage
    fi
    AUTH_ID=$2
    curl -X POST \
      -H "Authorization: Bearer $(gcloud auth print-access-token)" \
      -H "Content-Type: application/json" \
      -H "X-Goog-User-Project: ${PROJECT_NUMBER}" \
      -w "\nHTTP Status Code: %{http_code}\n" \
      "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/authorizations?authorizationId=${AUTH_ID}" \
      -d '{
        "name": "projects/'"${PROJECT_NUMBER}"'/locations/global/authorizations/'"${AUTH_ID}"'",
        "serverSideOauth2": {
          "clientId": "'"${OAUTH_CLIENT_ID}"'",
          "clientSecret": "'"${OAUTH_CLIENT_SECRET}"'",
          "authorizationUri": "'"${OAUTH_AUTH_URI}"'",
          "tokenUri": "'"${OAUTH_TOKEN_URI}"'"
        }
      }'
    ;;
  delete-auth)
    if [ $# -ne 2 ]; then
      echo "Error: delete-auth requires AUTH_ID argument."
      usage
    fi
    AUTH_ID=$2
    curl -X DELETE \
      -H "Authorization: Bearer $(gcloud auth print-access-token)" \
      -H "Content-Type: application/json" \
      -H "X-Goog-User-Project: ${PROJECT_NUMBER}" \
      -w "\nHTTP Status Code: %{http_code}\n" \
      "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/authorizations/${AUTH_ID}"
    ;;
    list)
    if [ $# -eq 2 ]; then
      # If a name parameter is provided, filter the results
      NAME=$2
      RESPONSE=$(curl -s -X GET \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        -H "X-Goog-User-Project: ${PROJECT_NUMBER}" \
        "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents")

      # Check if jq is installed
      if command -v jq &> /dev/null; then
        # Use jq to filter the response for the agent with the specified displayName
        # Make the search case-insensitive and allow partial matches
        FILTERED_RESPONSE=$(echo "$RESPONSE" | jq --arg name "$NAME" '{agents: [.agents[] | select(.displayName | ascii_downcase | contains($name | ascii_downcase))]}')

        # Check if any agents were found
        AGENT_COUNT=$(echo "$FILTERED_RESPONSE" | jq '.agents | length')
        if [ "$AGENT_COUNT" -eq 0 ]; then
          echo "No agents found with name containing '$NAME'."
          echo "Available agents:"
          echo "$RESPONSE" | jq '.agents[].displayName'
        else
          echo "$FILTERED_RESPONSE"
        fi
      else
        echo "Warning: jq is not installed. Displaying unfiltered results."
        echo "To filter results, please install jq: https://stedolan.github.io/jq/download/"
        echo "$RESPONSE"
      fi
    else
      # If no name parameter is provided, return all agents
      curl -X GET \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        -H "X-Goog-User-Project: ${PROJECT_NUMBER}" \
        "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents"
    fi
    ;;
  delete)
    if [ $# -ne 2 ]; then
      echo "Error: delete requires AGENT_ID argument."
      usage
    fi
    AGENT_ID=$2
    curl -X DELETE \
      -H "Authorization: Bearer $(gcloud auth print-access-token)" \
      -H "Content-Type: application/json" \
      -H "X-Goog-User-Project: ${PROJECT_NUMBER}" \
      "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents/${AGENT_ID}"
    ;;
  update)
    if [ $# -ne 4 ]; then
      echo "Error: update requires AGENT_ID, ADK_DEPLOYMENT_ID, and DISPLAY_NAME arguments."
      usage
    fi
    AGENT_ID=$2
    ADK_DEPLOYMENT_ID=$3
    NEW_DISPLAY_NAME=$4
    curl -X PATCH \
      -H "Authorization: Bearer $(gcloud auth print-access-token)" \
      -H "Content-Type: application/json" \
      -H "X-Goog-User-Project: ${PROJECT_NUMBER}" \
      "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents/${AGENT_ID}" \
      -d '{
        "displayName": "'"${NEW_DISPLAY_NAME}"'",
        "description": "'"${DESCRIPTION}"'",
        "adk_agent_definition": {
          "tool_settings": {
            "tool_description": "'"${TOOL_DESCRIPTION}"'"
          },
          "provisioned_reasoning_engine": {
            "reasoning_engine": "projects/'"${PROJECT_NUMBER}"'/locations/'"${LOCATION}"'/reasoningEngines/'"${ADK_DEPLOYMENT_ID}"'"
          }
        }
      }'
    ;;
  update-auth)
    if [ $# -ne 5 ]; then
      echo "Error: update-auth requires AGENT_ID, ADK_DEPLOYMENT_ID, AUTH_ID, and DISPLAY_NAME arguments."
      usage
    fi
    AGENT_ID=$2
    ADK_DEPLOYMENT_ID=$3
    AUTH_ID=$4
    NEW_DISPLAY_NAME=$5
    curl -X PATCH \
      -H "Authorization: Bearer $(gcloud auth print-access-token)" \
      -H "Content-Type: application/json" \
      -H "X-Goog-User-Project: ${PROJECT_NUMBER}" \
      "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents/${AGENT_ID}" \
      -d '{
        "displayName": "'"${NEW_DISPLAY_NAME}"'",
        "description": "'"${DESCRIPTION}"'",
        "adk_agent_definition": {
          "tool_settings": {
            "tool_description": "'"${TOOL_DESCRIPTION}"'"
          },
          "provisioned_reasoning_engine": {
            "reasoning_engine": "projects/'"${PROJECT_NUMBER}"'/locations/'"${LOCATION}"'/reasoningEngines/'"${ADK_DEPLOYMENT_ID}"'"
          },
          "authorizations": [
            "projects/'"${PROJECT_NUMBER}"'/locations/global/authorizations/'"${AUTH_ID}"'"
          ]
        }
      }'
    ;;
  *)
    usage
    ;;
esac
