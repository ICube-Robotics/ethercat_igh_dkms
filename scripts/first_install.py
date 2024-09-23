#! /usr/bin/env python3
import ethercat_igh_dkms as edkms
import sys
import subprocess
import traceback
import os
from pathlib import Path

import click

project_dir = Path(os.path.abspath(__file__)).parent.parent


def handle_subprocess_error(e, cmd, exit=True):
    res_out = e.stdout.decode() if e.stdout else "No stdout"
    res_err = e.stderr.decode() if e.stderr else "No stderr"
    imsg = f"ERROR: {cmd} failed with error: {e}, stdout: {res_out}, stderr: {res_err}"
    print(imsg, flush=True)
    edkms.get_logger().error(imsg)
    if exit:
        sys.exit(-1)


def display_file_content(file_path: str):
    try:
        with open(file_path, "r") as f:
            print(f.read(), flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)


@click.command()
@click.option('-i', '--interactive', type=bool, default=True, help='Interactive mode')
@click.option('--skip_dependencies', is_flag=True, show_default=True,  default=False, help='Do not install dependencies', required=False)
@click.option('--skip_secure_boot_check', is_flag=True, show_default=True, default=False, help='Skip the secure boot check', required=False)
def main(interactive, skip_dependencies=False, skip_secure_boot_check=False):
    proj_name = "ethercat_igh_dkms"
    log_dir = "/var/log/" + proj_name
    log_file = proj_name + ".init"

    # Log management
    ################
    edkms.create_logger(log_file, log_dir)
    imsg = "First install of EtherCAT IGH Master kernel modules and tools for Linux..."
    edkms.get_logger().info(imsg)
    if interactive:
        print(imsg, flush=True)

    if interactive:
        # Inform the user that parameters are defined in parameters.py
        proceed = False
        while not proceed:
            parameters_file = os.path.join(
                project_dir, "ethercat_igh_dkms", "parameters.py")
            ok = input(
                f"You use interactive mode configuration.\nFor most use cases, you should be able to proceed just by answering the following questions.\nHowever, some complex cases need specific configurations not possible with this interactive mode.\nIn these cases, please update the parameters in the file:\n{parameters_file}\n\nAfter having updated the configuration parameters (if you needed it), press\n\tI : if you want to run the install in interactive mode\n\tS : if you want to proceed without interactive mode\n\tX to abort.\n[I, S, X]: > ")
            if ok == "I":
                proceed = True
                edkms.set_interactive(True)
            elif ok == "X":
                imsg = "Aborted by user."
                edkms.get_logger().info(imsg)
                print(imsg)
                sys.exit(-1)
            elif ok == "S":
                proceed = True
                edkms.set_interactive(False)

    # Build and install the module
    ##############################
    try:

        imsg = "Building the ethercat igh kernel modules and tools ..."
        edkms.get_logger().info(imsg)
        if interactive:
            print(imsg, flush=True)
        # If the module was installed previously, remove it to have a clean install
        imsg = "Verify if a previous install in dkms is present ..."
        edkms.get_logger().info(imsg)
        if interactive:
            print(imsg, flush=True)
        cmd = ["dkms", "status"]
        try:
            result = subprocess.run(
                cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Check that the kernel modules are present in the lines of the output
            # get the lines of the output
            lines = result.stdout.decode().split("\n")
            n = "ethercat"
            v = edkms.get_version()

            # find the line containing "ethercat" and the version
            found_in_dkms_status = False
            for l in lines:
                if (n in l) and (v in l):
                    found_in_dkms_status = True
                    imsg = "A previous install in dkms is present. Remove it ..."
                    edkms.get_logger().info(imsg)
                    if interactive:
                        print(imsg, flush=True)
                    cmd = ["dkms", "remove", edkms.get_dkms_name(), "--all"]
                    try:
                        result = subprocess.run(
                            cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    except subprocess.CalledProcessError as e:
                        handle_subprocess_error(e, cmd)
        except subprocess.CalledProcessError as e:
            handle_subprocess_error(e, cmd)

        imsg = "Building the kernel modules a first time to gather information. This may take some time ..."
        edkms.get_logger().info(imsg)
        if interactive:
            print(imsg, flush=True)

        # Build the kernel modules a first time to gather information
        edkms.build_module(do_install_dependencies=not skip_dependencies,
                           check_secure_boot=not skip_secure_boot_check)
        imsg = "Create the DKMS configuration ..."
        edkms.get_logger().info(imsg)
        if interactive:
            print(imsg, flush=True)
        edkms.create_dkms_config()

        # Record kernel modules in DKMS
        imsg = "Adding the etherCAT project to DKMS ..."
        edkms.get_logger().info(imsg)
        dkms_conf_dir = edkms.def_source_dir()
        if interactive:
            print(imsg, flush=True)
        cmd = ["dkms", "add", dkms_conf_dir]
        result = None
        try:
            result = subprocess.run(
                cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            res_err = e.stderr.decode() if e.stderr else "No stderr"
            if "DKMS tree already contains" not in res_err:
                display_file_content(os.path.join(dkms_conf_dir, "dkms.conf"))
                handle_subprocess_error(e, cmd)

        # Build kernel modules with DKMS
        imsg = "Building the kernel modules with DKMS ..."
        edkms.get_logger().info(imsg)
        if interactive:
            print(imsg, flush=True)
        cmd = ["dkms", "build", edkms.get_dkms_name()]
        try:
            result = subprocess.run(
                cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            handle_subprocess_error(e, cmd)

        # Install kernel modules with DKMS
        imsg = "Installing the kernel modules with DKMS. This may take some time ..."
        edkms.get_logger().info(imsg)
        if interactive:
            print(imsg, flush=True)
        cmd = ["dkms", "install", edkms.get_dkms_name(), "--force"]
        try:
            result = subprocess.run(
                cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            handle_subprocess_error(e, cmd)

        if edkms.do_systemd_autoinstall():
            # Install the systemd service file
            pass

        # Check that everything is installed ok
        imsg = "Checking that the kernel modules are correctly installed with dkms ..."
        edkms.get_logger().info(imsg)
        if interactive:
            print(imsg, flush=True)
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
                            "Some kernel modules are correctly installed.")
                    else:
                        edkms.get_logger().error(
                            "ERROR: no kernel module is installed.")
                    break
            if not found_in_dkms_status:
                imsg = "ERROR: The kernel modules are not installed"
                edkms.get_logger().error(imsg)
                print(imsg, flush=True)
                sys.exit(-1)
        except subprocess.CalledProcessError as e:
            handle_subprocess_error(e, cmd)

        imsg = "\nSUCCESS:\n========\nEtherCAT IGH Master kernel modules and tools for Linux have been installed.\nDKMS is correctly configured, therefore a new version of the linux kernel should trigger an automatic recompilation of EtherCAT IGH Master kernel modules and tools."
        edkms.get_logger().info(imsg)
        if interactive:
            print(imsg, flush=True)
    except Exception as e:
        imsg = f"ERROR: ".join(
            traceback.TracebackException.from_exception(e).format())
        edkms.get_logger().error(imsg)
        print(imsg, flush=True)
        sys.exit(-1)


if __name__ == "__main__":
    main()
