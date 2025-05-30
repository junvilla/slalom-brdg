The Bridge Log Viewer provides an easy way to explore and troubleshoot Tableau Bridge logs by aggregating them in a single, searchable, filterable interface. This interface supports viewing logs from:

- Docker containers
- Local disk (such as Bridge installations on Windows)
- Kubernetes pods
With this feature, you can quickly filter logs by severity, search for specific text, and sort log rows to find relevant information faster.

## Capabilities

- Filter logs by severity, log file type, log event type, or any arbitrary text like "failed to refresh datasource".
- Ability for BridgeCtl to zip up bridge logs and download a single zip file.
- Search logs in-place in Docker or Kubernetes.

## Getting Started
#### Accessing the Log Viewer
From the BridgeCTL web UI, navigate to the Log Viewer page.
Select the log source type:
docker – if you want to browse logs from local Docker containers
disk – if you are viewing logs stored on a Windows machine (or a local filesystem)
k8s – if you are retrieving logs from a Kubernetes deployment (this feature must be enabled from Settings).

#### Choosing a Container (or File Location)
If you chose docker or k8s, select the container or pod name from the dropdown.
If you chose disk, specify the local path where your Bridge logs are stored.

#### Selecting a Log to View
Once you have chosen the container or disk location:

- Choose the specific log file from the dropdown.
- Select various filter criteria.

![image](https://github.com/user-attachments/assets/25127d1c-7344-45d3-81cb-261ccdec87b8)
