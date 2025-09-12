# Agentspace Auth

## Prerequisites
- Create agentspace `Client ID` and `Client SECRET` using GCP Auth Platform for `Web Application` type. Download the JSON file.

- Copy and paste to store the content of the client secret JSON in Google Secret Manager using key `AGENTSPACE_WEB_SECRET_JSON`.

- Go to IAM, grant Reasoning Engine service account permission `secretmanager.versions.access`.

- Choose a value of your choice, say `TEST_AUTH_ID`, and store the value in Google Secret Manager using key `AGENTSPACE_WEB_AUTH_ID`

- Create a GCS bucket name of your choice, say `MY_GCS_BUCKET`. The name need to be unique globally.

- Creata new Agentspace APP. One it is done, note down the `APP_ID` as shown below.
![image](assets/app_id.png)

## Part 1 - Create Agentspace Authentication ID
- Open `agent_registration.ipynb` notebook
- Update the PROJECT_ID and PROJECT_NUMBER following configuration in Step 1
    ```bash
    PROJECT_ID = "hello-world-418507"
    PROJECT_NUMBER = "671247654914"
    ```
- Execute all the cell for Step 1 and 2.
- Do not run Step 3, unless you want to delete the Authentication ID after the lab.

## Part 2 - Deploy ADK Agent to Agent Engine
- Open `ae_deploy.py`
- Update `ae_deploy.py` with the correct configuration values.
    ```python
    PROJECT_ID = "hello-world-418507"
    LOCATION = "us-central1"
    DISPLAY_NAME = "TEST_AUTH_ID"
    STAGING_BUCKET = "gs://MY_GCS_BUCKET"
    ```
- Deploy ADK agent to Agent Engine using `uv run ae_deploy.py`, this may take about 3mins.
- Once it is done, you will get a Reasoning `ENGINE_ID` as shown below.
![image](assets/engine_id.png)

## Part 3 - Register with Agentspace
- Update `configuration.sh` configuration, then run the script.
    ```bash
    export PROJECT_NUMBER="671247654914"
    export LOCATION="us-central1"
    export APP_ID="APP_ID" # APP_ID in prerequisite
    export ADK_DEPLOYMENT_ID="ENGINE_ID" # ENGINE_ID in Part 2
    export DESCRIPTION="You are a helpful assistant." # Optional
    export TOOL_DESCRIPTION="You are a helpful assistant." # Optional
    export DISPLAY_NAME="My custom ADK Agent" # Optional
    export OLD_AGENT_ID=111 # Optional. Leave it as 111, this is only useful when you want to delete a deployed agentspace custom agent
    ```
- Register ADK on Agent Engine to Agentspace using the command below
```bash
bash run_register_auth.sh
```
- Go to your Agentspace homepage, click Agents on the left menu, and click refresh.
- Now you should be able to see your custom ADK agent on Agentspace.


## Part 4 - Test the ADK Agent
- When you open the auth agent, you need to login to your personal email to test
- Authenticate with your personal email.
- Enter "get user info"
- Enter "send email to abc@gmail.com with subject:test, body: harlo"
