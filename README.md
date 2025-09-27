# Deploy Custom ADK Agent to Agentspace with authentication support.

## Repository Objective

This repository provides a complete solution for deploying custom ADK (Agent Development Kit) agents to Google Cloud's Agentspace platform with built-in authentication support. The primary goal is to enable developers to create, deploy, and register custom AI agents that can authenticate users via OAuth2 (using personal email accounts) and perform authorized actions on their behalf, such as accessing user information and sending emails. The repository streamlines the entire deployment pipeline from initial setup in Google Cloud Shell to final registration and testing in Agentspace.

## File Structure

The repository is organized into the following structure:
```text
.
├── auth_agent
│   ├── ae_deploy.py
│   ├── agent_registration.ipynb
│   ├── auth_agent
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── configuration.sh
│   ├── pyproject.toml
│   ├── register.sh
│   ├── run_register_auth.sh
│   └── uv.lock
└── README.md
```

### Root Level Files:
- **`README.md`** - Main documentation with step-by-step deployment instructions

### `/auth_agent/` Directory:

**Core Files:**
- **`ae_deploy.py`** - Python script for deploying the ADK agent to Agent Engine
- **`agent_registration.ipynb`** - Jupyter notebook for creating Agentspace Authentication ID
- **`configuration.sh`** - Shell script for setting environment variables and configuration
- **`run_register_auth.sh`** - Main script to execute the registration process with authentication
- **`register.sh`** - Helper script for the registration process

**Python Virtual Environment:**
- **`pyproject.toml`** - Python project configuration and dependencies
- **`uv.lock`** - Lock file for UV package manager dependencies

**`/auth_agent/auth_agent/` ADK Agent directory:**
- **`agent.py`** - Python package containing the actual ADK agent implementation:


## Prerequisites
- Create agentspace `Client ID` and `Client SECRET` using GCP Auth Platform for `Web Application` type. Download the JSON file.

- Copy and paste to store the content of the client secret JSON in Google Secret Manager using key `AGENTSPACE_WEB_SECRET_JSON`.

- Go to IAM, grant Reasoning Engine service account permission `secretmanager.versions.access`.

- Choose a unique name for authentication id, say `AUTH_ID=agentspace-lab1-auth-id`, note down the `AUTH_ID` in .env file.

- Creata new Agentspace app using console, say `APP_ID=agentspace-dev_1744685873939`, note down the `APP_ID` in .env file.
![image](assets/app_id.png)

- [TODO - automate] Create a GCS bucket name of your choice, say `STAGING_BUCKET=gs://2025-adk-workshop`, note down the `APP_ID` in .env file.


## Setup
- Open Cloud Shell, and click "Open Editor".

![image](assets/cloudshell.png)

- Open a terminal and then git clone the repo by running `git clone https://github.com/yapweiyih/alchemy-part1.git`.

![image](assets/terminal.png)

- Open the repo folder `alchemay-part1`.

![image](assets/open_folder.png)

## Part 0 - Update .env file
- Verify that you have updated the .env file, it should look as follows:

```bash
GOOGLE_CLOUD_PROJECT=hello-world-418507
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=1
DISPLAY_NAME=agentspace-lab1
APP_ID=agentspace-dev_1744685873939
AUTH_ID=agentspace-lab1-auth-id
STAGING_BUCKET=gs://2025-adk-workshop
```

## Part 1 - Deploy ADK Agent to Agent Engine
- Change directory `cd auth_agent`
- Run `uv run ae_deploy.py`, this may take about 3mins.
- Once it is done, you will get a Reasoning `ENGINE_ID` as shown below.
![image](assets/engine_id.png)
- Update the ENGINE_ID into .env manually
```bash
GOOGLE_CLOUD_PROJECT=hello-world-418507
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=1
DISPLAY_NAME=agentspace-lab1
APP_ID=agentspace-dev_1744685873939
AUTH_ID=agentspace-lab1-auth-id
STAGING_BUCKET=gs://2025-adk-workshop
ENGINE_ID=4256345850562740224
```

## Part 2 - Create Agentspace Authentication ID
- Run `uv run create_oauth_uri.py`
- This will create OAUTH URI and store in the .env file.
- Now your .env file should have a new entry `OAUTH_AUTH_URI`

```bash
GOOGLE_CLOUD_PROJECT=hello-world-418507
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=1
DISPLAY_NAME=agentspace-lab1
APP_ID=agentspace-dev_1744685873939
AUTH_ID=agentspace-lab1-auth-id
STAGING_BUCKET=gs://2025-adk-workshop
ENGINE_ID=4256345850562740224
OAUTH_AUTH_URI=...
```

## Part 3 - Register with Agentspace
- Run `bash register.sh create-auth` to create Agentspace authentication id. Make sure you success message `HTTP Status Code: 200`.
- Run `bash register.sh register-auth` to register ADK custom agent to Agentspace. Make sure you success message `"state": "ENABLED"`.
- Go to your Agentspace homepage, click Agents on the left menu, and click refresh.
- Now you should be able to see your custom ADK agent named `agentspace-lab1`.


## Part 4 - Test the ADK Agent
- When you open the `agentspace-lab1`, you will be asked to login to your email to authenticate
- Authenticate with your email.
- Enter "Check authentication"
- Enter "Send email to weiyih@google.com, subject: agentspace test, body: testing"


# Trouble shooting

## [OPTIONAL] Delete from Agentspace
- In the event there is problem and you need to register again, run `bash delete_agent.sh` to delete both Agentspace agent and authentication id.
- Now you can repeat Part 3.
