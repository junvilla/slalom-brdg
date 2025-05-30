## BridgeCTL Architecture Diagram

This page provides a comprehensive look at the architecture of BridgeCTL, including its components, workflows, and system interactions. Below is the architecture diagram and a detailed explanation of how the tool facilitates the deployment, monitoring, and management of Tableau Bridge Agents in containerized Docker and Kubernetes runtimes.

![image](https://github.com/user-attachments/assets/c2fd656a-d0d4-40ae-92a3-5f61282f492c)


# BridgeCTL Design
## Overview
BridgeCTL is a command-line utility designed to simplify the building, running, and monitoring of Tableau Bridge agents in containerized environments. It automates the image build process, including downloading and installing the necessary database drivers and Bridge RPM installer. BridgeCTL facilitates the configuration and deployment of Bridge containers in Docker or Kubernetes, and provides tools for monitoring agent health and viewing logs.

## Problem Statement
As organizations transition to containerized workflows, managing Tableau Bridge agents within these environments can be complex and resource-intensive. Customers often need assistance with building and deploying container images that are compatible with their existing container runtimes (e.g., Docker, AWS, GCP, Azure).

## High-Level Solution
BridgeCTL addresses these challenges by providing:

- Automation: Simplifies the creation of Docker images for Tableau Bridge agents, handling the download of necessary components and custom configurations.
- Flexibility: Supports deployment to various environments, including local machines, Docker containers, and Kubernetes clusters.
- Monitoring Tools: Offers features to monitor agent health, fetch logs, and analyze resource utilization directly from the customer's environment.
- Security: Ensures all sensitive data, such as Personal Access Tokens (PATs) and connection settings, are stored locally under the customer's control.

## Key Design Principles
- Security: All customer secrets are stored locally. No sensitive data is transmitted externally, ensuring compliance with security best practices.
- Self-Service Management: Empowers customers with full control over deployment and management processes, reducing reliance on external support.
- Scalability: Designed to support deployments ranging from single-agent setups to enterprise-scale Kubernetes clusters.
- Modularity: Features a layered architecture that separates core functionalities, allowing for independent updates and future extensibility.
- Cost-Effectiveness: Lightweight tool with minimal development and operational costs, leveraging open-source platforms for hosting and distribution.

## Architecture Components
### Command-Line Interface (CLI)
BridgeCTL operates through a CLI that runs locally on the customer's machine, inheriting the local security context. This ensures sensitive data remains within the customer's environment.

### Core Modules
- Startup Menu: Provides a guided interface for navigating commands and options.
- Token Manager: Manages Personal Access Tokens (PATs) generated in Tableau Cloud for agent authentication.
- Container Builder: Automates the creation of Docker images, including downloading database drivers and the Bridge RPM installer.
- Bridge Logs: Centralizes logging to fetch and analyze logs from various sources, with a customer-facing log viewer.
- Setup: Handles initial setup and updates.
- Docker and Kubernetes Clients: Manage interactions with Docker services and Kubernetes clusters, respectively.
- External Integrations
- Tableau Cloud API: Communicates with Tableau Cloud to retrieve settings, jobs, and agent statuses.
- Public Artifacts: Downloads necessary components from public repositories.


## Security Considerations
- Local Storage of Secrets: All sensitive data is stored locally. Customers are responsible for securing their local environment.
- No External Transmission of Sensitive Data: Only the Bridge agent communicates with Tableau Cloud for registration and operation.
- Encryption: Encrypt is recommended to secure sensitive information.

## Driver Caddy
BridgeCTL utilizes Driver Caddy, a framework for declaratively defining database driver installation scripts for containers. By specifying driver installation processes in YAML files, Driver Caddy allows for:
- Customization: Users can create and modify driver installation scripts according to their needs.
- Reusability: Shared scripts reduce duplication and simplify maintenance across different operating systems and drivers.
- Ease of Use: Simplifies the process of installing and testing database drivers in containerized environments.
