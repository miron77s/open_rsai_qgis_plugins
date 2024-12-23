# Open Remote Sensing AI Library QGIS Plugins (OpenRSAI-QGIS)

## Description

OpenRSAI-QGIS integrates the [OpenRSAI Algorithms](https://github.com/miron77s/open_rsai_algos) into QGIS environment to automate buildings, hydrography and greenery layers.

## Tutorial

The OpenRSAI-QGIS is the [Open Remote Sensing AI Library Core](https://github.com/miron77s/open_rsai) library extension that can be installed and tested in complex according the [tutorial](https://github.com/miron77s/open_rsai/blob/main/tutorial/TUTORIAL.md). 

## Hardware Requirements

OpenRSAI-Markup hardware requirements come up from [OpenRSAI-Core](https://github.com/miron77s/open_rsai#hardware) and [OpenRSAI-Algos](https://github.com/miron77s/open_rsai_algos#hardware) utilities requirements and are the following:


 - 16 Gb RAM.
 - NVIDIA GeForce 4070 (minimum 12Gb GPU memory).
 - 6Gb of free disk space.


## Installation Guide

Please follow these steps to install and activate the QGIS plugins from this repository on Ubuntu 22.04.

### 1. OpenRSAI-Algo Setup

Follow the OpenRSAI-Core [requirements](https://github.com/miron77s/open_rsai#requirements) and [build guide](https://github.com/miron77s/open_rsai#compile-and-installation-using-cmake), OpenRSAI-Algo [installation guide](https://github.com/miron77s/open_rsai_algos?tab=readme-ov-file#installation) to get automatic toolchains.

### 2. QGIS Setup

Before installing the plugins, ensure that QGIS is installed on your system. If QGIS is not installed, refer to the official QGIS installation guide (https://qgis.org/en/site/forusers/alldownloads.html#debian-ubuntu) for detailed instructions on how to install it on your Ubuntu system.

### 3. Plugins Copying to QGIS Plugins Directory

After ensuring that QGIS is properly installed, you can proceed to install the plugins. To do this, use the provided install.sh shell script which will automate the process of copying the plugin files to the correct QGIS plugins directory.

From the terminal, navigate to the root of the cloned repository and execute the script by running:

```
sh install.sh
```

## 4. Activating Plugins in QGIS

With the plugins now in the appropriate directory, the next step is to activate them within QGIS. Follow these instructions to activate the specific plugins:

1. Launch QGIS.
2. Navigate to `Plugins` > `Manage and Install Plugins...` in the menu bar.
3. In the `Installed` tab, look for the following plugins:
    - Buildings AI Detector
    - Greenery AI Detector
    - Hydro AI Detector
4. For each of the plugins listed above, find their names in the list and check the corresponding boxes to activate them.
5. Click 'OK' to confirm and the plugins will be activated and ready for use.

## Special Thanks

We wish to thank Innovations Assistance Fund (Фонд содействия инновациям, https://fasie.ru/)
for their support in our project within Code-AI program (https://fasie.ru/press/fund/kod-ai/).