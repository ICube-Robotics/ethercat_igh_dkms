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

1. the script `debian/ethercat_igh_dkms_init` is replaced by the script `debian/ethercat_igh_init`.
2. the script `scripts/first_install.py` is updated to remove the part that handles the modules with dkms.
3. the file   `debian/control` is updated to remove the dependency on dkms, change the package name to `ethercat-igh-install` and declare the conflict with the `ethercat-igh-dkms` package.
4. the file   `debian/changelog` is updated to reflect the change of the package name: `ethercat-igh-dkms` to `ethercat-igh-install`.
5. the script `debian/install` is updated to remove the dkms directory.
6. the script `debian/postrm` is updated to remove the part that handles the modules with dkms.
7. the folder `dkms` is removed.

