==================================
No dkms : developer documentation
==================================

.. _no_dkms_dev:

.. contents::
    :local:

------------
Introduction
------------

The differences between the dkms version and the no-dkms version happens in the following files:

1. the script `debian/ethercat_igh_dkms_init` is replaced by the script `debian/ethercat_igh_init`. The script is updated with new print messages.
2. the script `scripts/first_install.py` is updated to remove the part that handles the modules with dkms. The success message is updated.
3. the file   `debian/control` is updated to remove the dependency on dkms, change the package name to `ethercat-igh-install` and declare the conflict with the `ethercat-igh-dkms` package.
4. the file   `debian/changelog` is updated to reflect the change of the package name: `ethercat-igh-dkms` to `ethercat-igh-install`.
5. the script `debian/install` is updated to remove the dkms directory.
6. the script `debian/postrm` is updated to remove the part that handles the modules with dkms.
7. the folder `dkms` is removed.
8. Remove the elements relative to systemd and dkms in the `ethercat_igh_dkms/parameters.py` file.

----------------
Installed files
----------------

Files are installed in the following folders:
1. `/usr/share/ethercat_igh_dkms` the folder where the installer files are located (the files of this git repository)
2. `/usr/src/ethercat-version` with version being `stable-1.6` for instance, the folder where the source code of the EtherCAT IgH Master is located and where compilation is done.
3. `/usr/local/etherlab` the folder where the EtherCAT IgH Master library files are located.


----------------
Troubleshooting
----------------

..........................................................................
Error: «modprobe: ERROR: could not insert 'ec_generic': Exec format error»
..........................................................................

Check that there is no old version of the modules (here ec_generic) in the kernel modules directory 

``` bash
cd /lib/modules/$(uname -r)
find . -name ec_generic.ko
```



