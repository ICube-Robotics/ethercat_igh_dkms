#! /usr/bin/env python3
import ethercat_igh_dkms as edkms
import sys
import shutil


def main():
    proj_name = "ethercat_igh_dkms"
    log_dir = "/var/log/" + proj_name
    log_file = proj_name + ".clean"

    # Remove the build directory
    source_dir = edkms.def_source_dir()
    # shutil.rmtree(source_dir)


if __name__ == "__main__":
    main()
