[![Community Supported](https://img.shields.io/badge/Support%20Level-Community%20Supported-457387.svg)](https://www.tableau.com/support-levels-it-and-developer-tools)
[![GitHub](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://raw.githubusercontent.com/Tableau/TabPy/master/LICENSE)
# Installation on Redhat Enterprise Linux 9 (RHEL9) 


## Installation on RHEL9
BridgeCTL should technically work on any Linux distro with Python3.10 or newer and Docker or Podman installed. However, we only test on [RHEL9](./Installation_RHEL.md), [AmazonLinux2023](./Installation_AmazonLinux.md) and latest [Ubuntu LTS](./Installation_Ubuntu.md) 


## Prerequisites 
- Python >= 3.10
- Podman or Docker


## Install Podman

[Podman](https://docs.podman.io/en/latest/) as a drop-in alternative to Docker available in RHEL repositories. Podman installation is easier and packages are maintained by Redhat. Podman is also fully compatible with Docker and all docker commands are available. However, if you prefer Docker, or already have it installed, skip to the next section.


```bash
sudo dnf -y install podman-docker
``` 

> Running BridgeCTL as root is not the best idea. We need to allow current user to run Podman containers without root privileges. More details in [Podman github tutorials](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md)

```bash
sudo usermod --add-subuids 100000-165536 --add-subgids 100000-165536 $USER
``` 

Also, ensure that podman socket enabled and running  user and is exported as DOCKER_HOST
```bash
systemctl --user enable podman.socket
systemctl --user start podman.socket
systemctl --user status podman.socket
export DOCKER_HOST=unix:///run/user/$UID/podman/podman.sock
```

and finally add the export of DOCKER_HOST into users .bashrc (or any relevant rc file for your shel)
```bash
echo 'export DOCKER_HOST=unix:///run/user/$UID/podman/podman.sock' >> .bashrc 
```


## (Alternatively) Install Docker
Follow official Docker documentation for installation on [RHEL](https://docs.docker.com/engine/install/rhel).


> Running BridgeCTL as root is not the best idea. We need to allow current user to run Docker containers without root privileges, by adding user to the docker group

```bash
sudo usermod -a -G docker $USER
newgrp docker
```


## Install Python3.10 or newer

RHEL9 comes with Python 3.9.x preinstalled, but Python 3.11.x is available to be installed from the repository.
```bash
sudo dnf -y install python3.11
```

> **Note:** Keep in mind that Python 3.9.x is still installed and will be used as alias for python3 command. We need to execute python3.11 explicitly (or change the alias).


## Install BridgeCTL
BridgeCTL is easy to install. Just download and run the bridgectl_setup.py script using the following two commands:

```bash
python3.11 bridgectl_setup.py
```

## (Optional) Edit web UI server address (only needed if you don't have a local browser)
1) In a new terminal, enter the following command to start the BridgeCTL command-line:
```
bridgectl
```

2) From the BridgeCTL main menu, select "Edit App Settings" and then "Edit web UI server address"
Replace "localhost" with the machine hostname and press save. This will allow you to access the BridgeCTL web UI from another machine.

## Start UI

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
