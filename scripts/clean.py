#! /usr/bin/env python3
import ethercat_igh_dkms as edkms
import sys
import shutil


def main():
    proj_name = "ethercat_igh_dkms.clean"
    log_dir = "/var/log/" + proj_name

    # Remove the build directory
    source_dir = edkms.def_source_dir()
    # shutil.rmtree(source_dir)


if __name__ == "__main__":
    main()
