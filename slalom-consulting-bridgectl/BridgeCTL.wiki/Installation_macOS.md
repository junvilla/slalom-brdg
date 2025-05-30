[![Community Supported](https://img.shields.io/badge/Support%20Level-Community%20Supported-457387.svg)](https://www.tableau.com/support-levels-it-and-developer-tools)
[![GitHub](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://raw.githubusercontent.com/Tableau/TabPy/master/LICENSE)
# Installation on macOS


## Installation on macOS
Istructions were tested on macOS Sonoma 14.4.1, but should be compatible with older and newer releases.

## Prerequisites
- Python >= 3.10
- Docker (tested on Docker Desktop)

## Install Docker
Follow official Docker Desktop documentation for installation on [macOS](https://docs.docker.com/desktop/setup/install/mac-install).

## Install latest Python3 (>= Python3.10)
MacOS Sonoma comes with python3.9, follow official Python documentation for installation [macOS](hhttps://docs.python.org/3/using/mac.htm) to install latest version (>= 3.10).

In macOS you need to manyally install CA certificates, modify this command with the actual version of python you have installed (3.13 in this example)
```bash
open /Applications/Python\ 3.13/Install\ Certificates.command
```

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
