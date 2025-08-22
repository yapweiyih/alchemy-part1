#! /bin/env bash

source configuration.sh

echo
echo "********************* Variables *********************"
echo "PROJECT_NUMBER: ${PROJECT_NUMBER}"
echo "LOCATION: ${LOCATION}"
echo "APP_ID: ${APP_ID}"
echo "DESCRIPTION: ${DESCRIPTION}"
echo "TOOL_DESCRIPTION: ${TOOL_DESCRIPTION}"
echo "AUTH_ID: ${AUTH_ID}"
echo "DISPLAY_NAME: ${DISPLAY_NAME}"
echo "OLD_AGENT_ID: ${OLD_AGENT_ID}"
echo "ADK_DEPLOYMENT_ID: ${ADK_DEPLOYMENT_ID}"
echo "OAUTH_CLIENT_ID: ${OAUTH_CLIENT_ID}"
echo "OAUTH_CLIENT_SECRET: ${OAUTH_CLIENT_SECRET}"
echo "OAUTH_AUTH_URI: ${OAUTH_AUTH_URI}"
echo "OAUTH_TOKEN_URI: ${OAUTH_TOKEN_URI}"
echo "********************* Variables *********************"
echo

usage() {
  echo "Usage: $0 {register <ADK_DEPLOYMENT_ID> <DISPLAY_NAME>|list|delete <AGENT_ID>|register-auth <ADK_DEPLOYMENT_ID> <AUTH_ID> <DISPLAY_NAME>|create-auth <AUTH_ID>|delete-auth <AUTH_ID>|update <AGENT_ID> <ADK_DEPLOYMENT_ID> <DISPLAY_NAME>}"
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

    echo "Registering agent with auth_id ${AUTH_ID}..."
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
    curl -X GET \
      -H "Authorization: Bearer $(gcloud auth print-access-token)" \
      -H "Content-Type: application/json" \
      -H "X-Goog-User-Project: ${PROJECT_NUMBER}" \
      "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents"
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
  *)
    usage
    ;;
esac
