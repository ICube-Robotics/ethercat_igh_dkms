#! /usr/bin/env python3
import ethercat_igh_dkms as edkms
import sys
import subprocess

import click


@click.command()
@click.option('-i', '--interactive', type=bool, default=True, help='Interactive mode')
def first_install(interactive):
    proj_name = "ethercat_igh_dkms"
    log_dir = "/var/log/" + proj_name

    # Log management
    ################
    edkms.create_logger(proj_name, log_dir)
    edkms.get_logger().info(
        "First install of EtherCAT IGH Master kernel modules and tools for Linux...")

    if interactive:
        # Inform the user that parameters are defined in parameters.py
        proceed = False
        while not proceed:
            ok = input(
                "You use interactive mode configuration. For most use cases, you should be able to proceed just by answering the following questions.\n However, some complex cases need specific configurations not possible with this interactive mode. In this case, please update the parameters in the file ethercat_igh_dkms/parameters.py .\nAfter having updating parameters if you need it, press\n\tI : if you want to run the install in interactive mode\n\tS : if you want to proceed without interactive mode\n\tX to abort.\n[I, S, X]: > ")
            if ok == "I":
                proceed = True
                edkms.set_interactive(True)
            elif ok == "X":
                sys.exit(-1)
            elif ok == "S":
                proceed = True
                edkms.set_interactive(False)

    # Build and install the module
    ##############################
    try:
        edkms.build_module()
        edkms.create_dkms_config()

        # Record kernel modules in DKMS
        cmd = ["dkms", "add", edkms.def_source_dir()]
        try:
            result = subprocess.run(
                cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            edkms.get_logger().error(
                f"ERROR: {cmd} failed with error: {e}")
            sys.exit(-1)

        # Build kernel modules with DKMS
        cmd = ["dkms", "build", edkms.get_dkms_name()]
        try:
            result = subprocess.run(
                cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            edkms.get_logger().error(
                f"ERROR: {cmd} failed with error: {e}")
            sys.exit(-1)

        # Install kernel modules with DKMS
        cmd = ["dkms", "install", edkms.get_dkms_name()]
        try:
            result = subprocess.run(
                cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            edkms.get_logger().error(
                f"ERROR: {cmd} failed with error: {e}")

        # Check that everything is installed ok
        cmd = ["dkms", "status"]
        try:
            result = subprocess.run(
                cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            edkms.get_logger().info(result.stdout.decode())
            # Check that the kernel modules are present in the lines of the output
            # get the lines of the output
            lines = result.stdout.decode().split("\n")
            n = "ethercat"
            v = edkms.get_version()
            ker = edkms.get_kernel()

            # find the line containing "ethercat" and the version
            found_in_dkms_status = False
            for l in lines:
                if (n in l) and (v in l) and (ker in l):
                    found_in_dkms_status = True
                    if "installed" in l:
                        edkms.get_logger().info(
                            "The kernel modules are correctly installed.")
                    else:
                        edkms.get_logger().error(
                            "ERROR: The kernel modules are not installed.")
                    # TODO check that all the kernel modules expected are present
                    break
            if not found_in_dkms_status:
                edkms.get_logger().error(
                    "ERROR: The kernel modules are not installed.")
                sys.exit(-1)

        except Exception as e:
            edkms.get_logger().error(
                f"ERROR: {cmd} failed with error: {e}")
            sys.exit(-1)

        edkms.get_logger().info(
            "SUCCESS: EtherCAT IGH Master kernel modules and tools for Linux have been installed.")
    except Exception as e:
        sys.exit(-1)


if __name__ == "__main__":
    first_install()
