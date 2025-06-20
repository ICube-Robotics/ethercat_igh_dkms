# Debian installer for the EtherCAT Master stack of IgH

This is a Debian package that installs the EtherCAT Master stack of IgH.
The package is based on the source code of the EtherCAT Master stack of IgH

## Installation
Download the file ethercat-igh-install_1.0_arm64.deb in the `/tmp` folder and install it with the following command:
```sudo apt -f install ./ethercat-igh-install_1.0_amd64.deb```

## Use
Then you can use the install script to install the EtherCAT Master stack of IgH:

``` bash
sudo ethercat_igh_init
```

You just have to follow the instructions of the script.
Every parameter is in the file 
`/usr/share/ethercat_igh_dkms/ethercat_igh_dkms/parameters.py`

The default installation and parameters install the EtherCAT Master stack of IgH with the following parameters:
1. generic driver
2. version: stable-1.6
3. 1 master
4. the program guess the right ethernet interface
5. 1 ethernet interface selected in that order: ethX, enoX, ensX, enpXsY, enxFF:FF:FF:FF:FF:FF

If you want to let the program give you the choice for the ethernet interface, in the file `/usr/share/ethercat_igh_dkms/ethercat_igh_dkms/parameters.py` you have to set the parameter `guess_used_ethernet_interface` to `False`.

If some configuration is present, like when you have already installed the EtherCAT Master stack of IgH and you need to update your installation for a new linux kernel the script will reuse the installed configuration file and not ask any question.

If you want to bypass this behaviour and force the script to reconstruct the configuration file `/etc/sysconfig/ethercat` use:
``` bash
sudo ethercat_igh_init -o
```

## Other options

* `--skip_dependencies`: to skip dependency installation (build-essential, git, etc.)
* `skip_secure_boot_check`: to skip the secure boot check
* `-i, --interactive`: to force the script to be interactive or to be non-interactive (e.g. `sudo ethercat_igh_init --interactive false`)



## Help
To see the help message you can use the following command:
``` bash
sudo ethercat_igh_init --help
```

## Uninstall
If you need to change the installation, please uninstall the package and reinstall it. To uninstall the package use the following command:
``` bash
sudo dpkg --purge ethercat-igh-install
```

## Manually build the debian package
We suppose that you work on a Debian based distribution like Ubuntu with an amd64 architecture.

``` bash
dh_clean
dpkg-buildpackage -us -uc
```

The debian package (example: ethercat-igh-install_1.0_amd64.deb) will be in the parent folder of the source code folder.

## Features

- [x] Create a Debian package for the EtherCAT Master stack of IgH
- [x] Allows to control the installation parameters with a configuration file
- [x] Allows to control if the installation is interactive with a script option
- [x] Allows to control if the installation will reuse already configured files with a script option
- [x] Add a `--help` option to the install script
- [x] Modify the code to be able to build the Debian package for a RPi (tested on a RPi 5 with Ubuntu Noble, see branch [x86-arm64-debian-no-dkms](https://github.com/ICube-Robotics/ethercat_igh_dkms/tree/x86-arm64-debian-no-dkms) )

## Roadmap
- [ ] Create a Debian package for the EtherCAT Master stack of IgH with the RT-Preempt patch
- [ ] Create a Debian package for the EtherCAT Master stack of IgH with the Xenomai patch