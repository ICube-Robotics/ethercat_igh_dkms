#! /usr/bin/env python3
import ethercat_igh_dkms as edkms
import sys


def main():
    proj_name = "ethercat_igh_dkms.build"
    log_dir = "/var/log/" + proj_name

    # Log management
    ################
    edkms.create_logger(proj_name, log_dir)

    # Build and install the module
    ##############################
    try:
        edkms.build_module()
    except Exception as e:
        sys.exit(-1)


if __name__ == "__main__":
    main()
