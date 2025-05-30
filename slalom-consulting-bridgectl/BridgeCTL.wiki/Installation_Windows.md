[![Community Supported](https://img.shields.io/badge/Support%20Level-Community%20Supported-457387.svg)](https://www.tableau.com/support-levels-it-and-developer-tools)
[![GitHub](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://raw.githubusercontent.com/Tableau/TabPy/master/LICENSE)
# Installation on Windows


## Installation on Windows
> **Note** this instructions are untested, but should work. I will test it and update soon as I get access to Windows machine capable to run Docker, WSL2 or Hyper-V.


## Prerequisites
- Python >= 3.10
- Docker (tested on Docker Desktop)

## Install Docker
Follow official Docker Desktop documentation for installation on [Windows](https://docs.docker.com/desktop/setup/install/windows-install).
> **Note** Installation of docker on windows requires either Hyper-V or WSL2.

## Install latest Python3 (>= Python3.10)
Follow official Python documentation, download from [Python download](https://www.python.org/downloads/windows/).

## Install BridgeCTL
BridgeCTL is easy to install. Just download and run the bridgectl_setup.py script using the following two commands:

```
curl -OL https://github.com/tab-se/bridgectl/releases/download/setup/bridgectl_setup.py
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
