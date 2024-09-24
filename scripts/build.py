#! /usr/bin/env python3
import ethercat_igh_dkms as edkms
import sys
import click


@click.command()
@click.option('--skip_dependencies', is_flag=True, show_default=True,  default=False, help='Do not install dependencies', required=False)
@click.option('--check_secure_boot', is_flag=True, show_default=True, default=False, help='Check secure boot', required=False)
@click.option('--kernel_sources', type=str, default=None, help='Path to kernel sources', required=False)
def main(skip_dependencies=False, check_secure_boot=False, kernel_sources=None):
    proj_name = "ethercat_igh_dkms"
    log_dir = "/var/log/" + proj_name
    log_file = proj_name + ".build"

    # Log management
    ################
    edkms.create_logger(log_file, log_dir)

    # Build and install the module
    ##############################
    try:
        edkms.build_module(do_install_dependencies=not skip_dependencies,
                           check_secure_boot=check_secure_boot, kernel_sources=kernel_sources)
    except Exception as e:
        sys.exit(-1)


if __name__ == "__main__":
    main()
