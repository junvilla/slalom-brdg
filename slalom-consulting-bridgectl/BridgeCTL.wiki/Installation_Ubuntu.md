[![Community Supported](https://img.shields.io/badge/Support%20Level-Community%20Supported-457387.svg)](https://www.tableau.com/support-levels-it-and-developer-tools)
[![GitHub](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://raw.githubusercontent.com/Tableau/TabPy/master/LICENSE)
# Installation on RHEL9 and Ubuntu 22.04


## Installation on Ubuntu 22.04
BridgeCTL should technically work on any Linux distro with Python3.10 or newer and Docker or Podman installed. However, we only test on [RHEL9](./Installation_RHEL.md), [AmazonLinux2023](./Installation_AmazonLinux.md) and latest [Ubuntu LTS](./Installation_Ubuntu.md)


## Prerequisites 
- Python >= 3.10
- Python3-venv
- Docker

## Install Docker
Follow official Docker documentation for installation on [Ubuntu](https://docs.docker.com/engine/install/ubuntu).

> Running BridgeCTL as root is not the best idea. We need to allow current user to run Docker containers without root privileges, by adding user to the docker group

```bash
sudo usermod -a -G docker $USER
newgrp docker
```

## Install Python3.10 ond venv

Ubuntu 22.04 comes with Python 3.10 pre-installed. However, Ubuntu does not bundle venv with Python3.10 anymore. You need to install it:
```bash
sudo apt update
sudo apt -y install python3-venv
```


## Install BridgeCTL
BridgeCTL is easy to install. Just download and run the bridgectl_setup.py script using the following two commands:

```bash
python3 bridgectl_setup.py
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
