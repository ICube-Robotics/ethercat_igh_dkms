#! /usr/bin/env python3
import ethercat_igh_dkms as edkms
import sys


def main():
    proj_name = "ethercat_igh_dkms"
    log_dir = "/var/log/" + proj_name
    log_file = proj_name + ".install"

    # Log management
    ################
    edkms.create_logger(log_file, log_dir)

    # Build and install the module
    ##############################
    try:
        edkms.install_module()
    except Exception as e:
        sys.exit(-1)


if __name__ == "__main__":
    main()
