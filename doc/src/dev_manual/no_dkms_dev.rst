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
2. the script 'debian/control' is updated to remove the dependency on dkms.
3. the script `debian/install` is updated to remove the dkms directory.
4. the script 'debian/postinst' is updated to remove the part that handles the modules with dkms.
5. the script `debian/postrm` is updated to remove the part that handles the modules with dkms.

