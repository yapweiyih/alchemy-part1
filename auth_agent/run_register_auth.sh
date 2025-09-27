#! /bin/env bash

########################################################
# UPDATE CONFIGURATION HERE
########################################################

# Source environment variables from .env file
source .env

# Print out the configuration
echo "run_register.sh config:"
echo "  ADK_DEPLOYMENT_ID: $ENGINE_ID"
echo "  DISPLAY_NAME: $DISPLAY_NAME"
echo "  AUTH_ID: $AUTH_ID"
echo
########################################################

# Delete existing ADK Agent with the same DISPLAY NAME if any
OLD_AGENT_ID=$(bash register.sh list ${DISPLAY_NAME} | grep "name" | grep -o '/agents/[0-9]*' | cut -d'/' -f3)

echo "**********************************************"
echo "Delete old agentspace agent: $OLD_AGENT_ID"
bash register.sh delete $OLD_AGENT_ID
echo

echo "**********************************************"
echo "Delete AUTH_ID: $AUTH_ID"
bash register.sh delete-auth $AUTH_ID
echo

echo "**********************************************"
echo "Creating Agentspace AUTH_ID: $AUTH_ID"
bash register.sh create-auth $AUTH_ID
echo

echo "**********************************************"
echo "Registering new reasoning engine to Agentspace: $ADK_DEPLOYMENT_ID, auth_id ${AUTH_ID}..."
bash register.sh register-auth $ADK_DEPLOYMENT_ID $AUTH_ID $DISPLAY_NAME
echo
