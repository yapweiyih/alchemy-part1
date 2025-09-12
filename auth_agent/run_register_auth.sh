#! /bin/env bash

source configuration.sh

# Delete existing registered agentspace agent
# bash register.sh delete $OLD_AGENT_ID

# Delete existing auth
# bash register.sh delete-auth $AUTH_ID

# Create new auth
bash register.sh create-auth $AUTH_ID

# Register new agentspace agent with auth
bash register.sh register-auth $ADK_DEPLOYMENT_ID $AUTH_ID $DISPLAY_NAME
