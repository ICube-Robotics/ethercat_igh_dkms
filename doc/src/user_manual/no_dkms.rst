=======
No dkms
=======


This version of the package does not use DKMS. The kernel modules are built and install by the ethercat_igh_init script. The kernel modules are built and installed for the running kernel. If the kernel is updated, the kernel modules must be rebuilt and reinstalled. This is done by running the ethercat_igh_init script again.
