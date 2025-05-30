# Run Tableau Bridge Containers in Local Docker

This page allows you to run Tableau Bridge containers in your local Docker environment. Follow these instructions to set up and run Bridge agents.

## Prerequisites
- Docker installed and running on your local machine
- Access to Tableau Bridge settings
- Personal Access Tokens (PAT) for authentication

## Instructions

1. **Build Image**
   - Build a local bridge container image on the build page. Select which drivers you'd like to install in the container, and which Tableu Bridge RPM version.

2. **Add Personal Access Tokens (PAT)**
   - Navigate to the Settings page
   - Add a PAT token for each bridge agent
   - Add one additional token starting with "admin-pat"

3. **Run a Bridge Container in local docker**
   - On the Run Page, click the "Edit" button to select a target pool for the bridge agents
   - Select one of the bridge images you built from the step above.
   - To Run Bridge container(s): Select one or more PAT tokens and click Run Bridge Containers. 


## Notes
- Ensure you have built a bridge image before attempting to run containers
- Each bridge agent requires its own unique PAT token for authentication
- The bridge container runs in local Docker container
- The bridge agent name and the docker container will match the name of the selected token

## Screenshot
<img width="783" alt="image" src="https://github.com/user-attachments/assets/9eca175b-feae-4d57-af27-d2bbae06e157" />

