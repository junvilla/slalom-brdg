[![Community Supported](https://img.shields.io/badge/Support%20Level-Community%20Supported-457387.svg)](https://www.tableau.com/support-levels-it-and-developer-tools)
[![GitHub](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://raw.githubusercontent.com/Tableau/TabPy/master/LICENSE)
# Installation on Amazon Linux 2023 (AL2023)


## Installation on AL2023
BridgeCTL should technically work on any Linux distro with Python3.10 or newer and Docker or Podman installed. However, we only test on [RHEL9](Installation_RHEL), [AmazonLinux2023](Installation_AmazonLinux) and latest [Ubuntu LTS](Installation_Ubuntu)


## Prerequisites 
- Python >= 3.10
- Docker


## Install Docker
AL2023 provides Docker from their own repository. If instructions bellow doesn't works, check the official [AWS documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-docker.html#install-docker-instructions)

```bash
sudo yum -y install docker
sudo service docker enable
sudo service docker start
```

> Running BridgeCTL as root is not the best idea. We need to allow current user to run Docker containers without root privileges, by adding user to the docker group

```bash
sudo usermod -a -G docker $USER
newgrp docker
```

## Install Python3.10 or newer
AL2023 comes with Python 3.9.x preinstalled, but Python 3.11.x is available to be installed from the repository.
```bash
sudo yum -y install python3.11
```

> **Note:** Keep in mind that Python 3.9.x is still installed and will be used as alias for python3 command. We need to execute python3.11 explicitly (or change the alias).


## Install BridgeCTL
BridgeCTL is easy to install. Just download and run the bridgectl_setup.py script using the following two commands:

```bash
curl -OL https://github.com/tab-se/bridgectl/releases/download/setup/bridgectl_setup.py
python3.11 bridgectl_setup.py
```

If installation is successful you should see menu bellow, you can head to the [Usage](./Usage.md) section for more detail:
```
starting BridgeCTL
___________     ___.   .__
\__    ___/____ \_ |__ |  |   ____ _____   __ __
  |    |  \__  \ | __ \|  | _/ __ \\__  \ |  |  \
  |    |   / __ \| \_\ \  |_\  ___/ / __ \|  |  /
  |____|  (____  /___  /____/\___  >____  /____/
               \/    \/          \/     \/

Bridge CTL - A utility to build, run and monitor Tableau Bridge Agents in Containers
BridgeCTL version 2.3.19 is up-to-date

App settings not found. Creating new ...
created new config at /home/ubuntu/bridgectl/config/bridge_settings.yml
? Main Menu (Use arrow keys)
 » Start UI
   Stop UI
   Edit App Settings
   Help ->
   Quit
```
