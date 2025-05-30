[![Community Supported](https://img.shields.io/badge/Support%20Level-Community%20Supported-457387.svg)](https://www.tableau.com/support-levels-it-and-developer-tools)
[![GitHub](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://raw.githubusercontent.com/Tableau/TabPy/master/LICENSE)
# Installation

This section will guide you through the installation process. Instructions bellow are bare minimum to run the BridgeCTL on Windows, macOS and Linux. For more detailed installation on Ubuntu and RHEL Linux, follow:
- Installation on [RHEL9](./Installation_RHEL.md), [AnazonLinux2023 Linux](./Installation_AmazonLinux.md) or [Ubuntu](./Installation_Ubuntu.md) Linux
- Installation on [Windows](./Installation_Windows.md)
- Installation on [macOS](./Installation_macOS.md)

## Prerequisites
- Python >= 3.10
- Docker (or Podman on RHEL9)
- BridgeCTL works on Windows, Linux or Mac

## Installation Steps
> **Note:** Python 3.10 or greater is required. Please use the appropriate python command on your machine to run the setup script, for example instead of **"python"** you may need to use **"python3"** or **"python3.11"**.
The BridgeCTL setup script will create a folder "bridgectl" in the current directory and a python virtual environment named "tabenv". It will then create a shortcut function `bridgectl` so that you can conveniently use that global command from the terminal.

BridgeCTL is easy to install. Just download and run the bridgectl_setup.py script using the following two commands:

```bash
python bridgectl_setup.py
```


