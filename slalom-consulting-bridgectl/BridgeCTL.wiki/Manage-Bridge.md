The Manage Bridge page is a centralized interface to manage local Docker bridge containers. It offers an overview of running bridge containers and tools to view metadata, perform administrative tasks, and manage bridge configurations.

## Bridge Container Details
This feature helps you monitor the container's configuration and health at a glance. The Details button provides a detailed view of the running container's metadata, including:
- Image Name: The Docker image being used by the container.
- Installed Drivers: A list of drivers installed within the container.
- Resource Utilization: Information on CPU, memory, and storage usage.
- Uptime: The duration for which the container has been actively running.

## Bridge logs
The Logs button displays the Docker logs (stdout) for the selected container. These logs offer insights into:
- A summary of Bridge refresh jobs recently executed by the bridge agent.
- Any error messages or warnings related to the jobs.
- Bridge connectivity errors

## Remove container
The Remove Container action performs the following steps:
- Stops and removes the local Docker bridge container.
- Unregisters the Bridge Agent by communicating with the Tableau Cloud API.
This feature is useful when decommissioning a bridge agent or replacing it with a new container instance.

## Bridge Client Configuration
The Manage Bridge page also provides access to the Bridge Client Configuration. Here, you can:
- Modify client-specific settings related to the bridge agent. After saving settings the bridge container will be restarted.

## Update Image
Update multiple bridge agents in Docker. The old containers will be removed and a new container will be started using the new image but with the same Pool and PAT Token settings. Bridge containers targeting a different pool will not be updated. Note that bridge logs inside the container will not be retained. Also note that sometimes PAT tokens become invalid but it does not become obvious until a container is restarted. If this happens simply create a new replacement PAT token from the Tableau UI.

## Scale Up
Select a target number of bridge containers to scale up or down the number of local bridge containers in docker.


## Screenshot

![image](https://github.com/user-attachments/assets/5e825578-3ef6-4f78-b160-beb020b46a8b)
