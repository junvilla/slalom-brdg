# Run Tableau Bridge Pods in Kubernetes

This page guides you through running Tableau Bridge pods in your Kubernetes cluster. Follow these instructions to set up and run Bridge agents in a Kubernetes environment.

## Prerequisites
- Access to a Kubernetes cluster
- Kubernetes context configured (kubectl)
- Access to Tableau Bridge settings in Tableau Cloud
- Personal Access Tokens (PAT) for authentication

## Instructions

1. **Select Kubernetes Context**
   - On the Settings -> Kubernetes page, ensure your Kubernetes context is configured
   - Select the k8s namespace where Bridge pods will be deployed

2. **Configure Bridge Pool**
   - Click the "Edit" button to select a Target Bridge Pool 
   - Select a target pool for your bridge agents.
     
     Note that this is the same bridge Pool used on the [Run Bridge in Docker Page](./Run-Bridge-In-Docker.md)

3. **Select Container Image**
   - Choose a Container Image Registry: "Local" or "AWS ECR". You can choose "Local" if your image has already been downloaded to your k8s cluster, for example if you are running K8s in local Docker. Select "AWS ECR" to download the image from the remote container registry before starting the k8s pod.
   - Example bridge image name: `tableau_bridge_rhel9_20243.25.0114.1153_mysuffix:latest`

4. **Add Personal Access Tokens (PAT)**
   - Select the PAT tokens to use for Bridge agent authentication. Each Bridge pod requires its own unique PAT token
   - The number of tokens selected determines the number of Bridge pods started.

5. **Run Bridge Pods**
   - Click "Run Bridge Agent Pods" to deploy the pods to your Kubernetes cluster
   - Pods will be created in the selected namespace
   - Each pod will be named based on its corresponding PAT token

## Notes
- Ensure your Kubernetes cluster has access to pull the Bridge container image if you selecct AWS ECR as your Container Registry.
- Monitor pod status through your standard Kubernetes tools (kubectl, dashboard, etc.)
- Bridge agents will automatically register with the specified Tableau Cloud Site and Pool when started

## Screenshot
![image](https://github.com/user-attachments/assets/68cf0a5e-02a7-4717-9cce-f80916750546)
