==============
Test Procedure
==============

1. Start with a kernel x.y.z where an other stable kernel x1.y1.z1 is available with x1.y1.z1 > x.y.z.
2. Install the debian package ethercat-igh-dkms_x.y.z_arch.deb
   1. Verify that no older version is installed and if so, remove it.  
``` bash
sudo dpkg --purge ethercat-igh-dkms
```
    1. Verify that either dkms is not installed or that if dkms is installed, no ethercat set of modules are installed
``` bash
sudo dkms status | grep ethercat
```
If the command fails, dkms is not installed. If the command returns nothing, no ethercat set of modules are installed. Otherwise remove the ethercat set of modules.
``` bash
sudo dkms remove -m ethercat/version --all
```
Remplacing ``version`` by the version of the ethercat set of modules appearing in the output of the previous command.
    1. Install the debian package
``` bash
sudo apt install ./ethercat-igh-dkms_x.y.z_arch.deb
```
1. Install/Force reinstall the kernel x1.y1.z1
To see the available kernels:
``` bash
dpkg --list | grep linux-image
dpkg --list | grep linux-headers
```
To install the kernel x1.y1.z1:
``` bash
sudo apt install --reinstall linux-image-x1.y1.z1-generic linux-headers-x1.y1.z1-generic
```
1. Reboot the system
2. Launch dkms autoinstall
``` bash
sudo dkms autoinstall
```
1. Verify that the ethercat set of modules is installed and the output of the command is successful
