#! /bin/env bash

########################################################
# UPDATE CONFIGURATION HERE
########################################################

export ADK_DEPLOYMENT_ID=7028311421209280512 # This is the new reasoning engine id
export DISPLAY_NAME=agentspace-lab1
export AUTH_ID=agentspace-lab1-auth-id
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
