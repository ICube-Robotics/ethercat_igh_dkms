import os
import sys
import subprocess
import shutil
import logging
from logging import Logger
from typeguard import typechecked
import re
from pathlib import Path

from .parameters import *
from .get_mac import *
from .get_hw_info import *

# Get the current kernel version
kernel_version = subprocess.check_output(["uname", "-r"]).strip().decode()

logger = None


@typechecked
def keep_one_file_log_history(logger_name: str, log_file_path: str):
    # Keep only one log file
    log_files = [f for f in os.listdir(log_file_path) if f.endswith(".log")]
    if 1 < len(log_files):
        # Sort the log files by date
        log_files.sort(key=lambda x: os.path.getmtime(
            os.path.join(log_file_path, x)))
        # Remove all log files except the most recent one
        for log_file in log_files[:-1]:
            os.remove(os.path.join(log_file_path, log_file))
    # Rename the remaining log file appending _prev to its base name
    if 1 <= len(log_files):
        remaining_file = log_files[-1]
        os.rename(os.path.join(log_file_path, remaining_file),
                  os.path.join(log_file_path, remaining_file.replace(".log", "_prev.log")))


@typechecked
def init_logging(logger_name: str, log_file_path: str) -> Logger:
    # Setup logging service
    logger = Logger.manager.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(os.path.join(log_file_path, logger_name + ".log"))
    fh.setLevel(logging.DEBUG)
    # create formatter and add it to the handler
    formatter = logging.Formatter(
        '%(asctime)s - logger : %(name)s - %(levelname)s - psid : %(processName)s - filename : %(filename)s - funcname: %(funcName)s - Line num : %(lineno)d -> %(message)s')
    fh.setFormatter(formatter)
    # add the handler to logger
    logger.addHandler(fh)
    #
    logger.info('Logger initialized !')
    return logger


@typechecked
def interactively_define_ethernet_interfaces() -> list:
    pass


@typechecked
def check_master_devices_key(k: str) -> bool:
    # A key should have the form: MASTER[0-9]+_DEVICE
    return re.match(r"MASTER[0-9]+_DEVICE", k) is not None


@typechecked
def check_hex_mac_address(mac: str) -> bool:
    # A MAC address should have the form: XX:XX:XX:XX:XX:XX
    return re.match(r"([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}", mac) is not None


@typechecked
def interactively_choose_master_devices(logger: Logger) -> dict:
    print("\n\nAvailable Ethernet interfaces:")
    print("-------------------------------\n")
    available_interfaces = identify_ethernet_interfaces(logger)
    for i, interface in enumerate(available_interfaces):
        print(f"\t{i+1}. {interface}")
        hw_addr = get_hw_info(interface, logger)
        if None != hw_addr:
            hw_type = get_hw_type(interface, logger)
            if EthernetHardwares.UNKNOWN != hw_type:
                info = get_more_hw_info(hw_addr, hw_type, logger)
                if None != info:
                    print(info)
        print()
    print("\n\nSummary:")
    for i, interface in enumerate(available_interfaces):
        print(f"\t{i+1}. {interface}")
    choice_recognized = False
    while not choice_recognized:
        user_choice = input(
            "Enter the interfaces you want to use with their index separated by ';': > ")
        try:
            user_choice = [int(x)
                           for x in user_choice.split(";")]
            for c in user_choice:
                if c <= 0 or c-1 > len(available_interfaces):
                    print(f"Invalid choice: {c}")
                    raise ValueError
            choice_recognized = True
        except ValueError:
            pass
    # choice_recognized is True
    master_devices = {}
    for i, c in enumerate(user_choice):
        mac = get_mac_address(
            logger, available_interfaces[c-1])
        if mac is not None:
            master_devices["MASTER" +
                           str(i)+"_DEVICE"] = mac
        else:
            print(
                f"Could not get the MAC address for interface {available_interfaces[c-1]}")
            logger.error(
                f"Could not get the MAC address for interface {available_interfaces[c-1]}")
            raise Exception(
                f"Could not get the MAC address for interface {available_interfaces[c-1]}")
    return master_devices


@typechecked
def ethernet_interfaces_are_valid(interfaces: list, logger: Logger) -> bool:
    """ Check if the interfaces are valid and MAC addresses can be found

    Parameters
    ----------
    interfaces : list
        List of Ethernet interfaces to check, each interface is a string
    logger : Logger
        Logger object to log messages
    """
    available_interfaces = get_all_interfaces(logger)

    for i in interfaces:
        if i not in available_interfaces:
            return False
        # Check if the MAC address can be found
        mac = get_mac_address(logger, i)
        if mac is None:
            return False
    return True


@typechecked
def update_ethercat_config(cfg_file: str):
    global used_ethernet_interfaces, logger, MASTER_DEVICES, guess_used_ethernet_interface, interactive, known_device_modules, device_modules
    # Find the configuration parameters
    # Check if the MASTER_DEVICES dictionary is defined
    to_use_master_devices = None
    if MASTER_DEVICES is not None:
        # Then the parameter superseeds all the others
        # Check if the dictionary contains correct values
        for k, v in MASTER_DEVICES.items():
            if not check_master_devices_key(k):
                logger.error(f"Invalid key in MASTER_DEVICES: {k}")
                raise Exception("Invalid key in MASTER_DEVICES")
            if not check_hex_mac_address(v):
                logger.error(f"Invalid value in MASTER_DEVICES: {v}")
                raise Exception("Invalid value in MASTER_DEVICES")
        to_use_master_devices = MASTER_DEVICES
    else:
        if used_ethernet_interfaces is not None:
            to_use_master_devices = {}
            # Then the parameter superseeds all the others
            # Check if the values are correct
            for i, interface in enumerate(used_ethernet_interfaces):
                mac = get_mac_address(logger, interface)
                if mac is not None:
                    to_use_master_devices["MASTER"+str(i)+"_DEVICE"] = mac
                else:
                    logger.error(
                        f"Could not get the MAC address for interface {interface}")
                    raise Exception(
                        f"Could not get the MAC address for interface {interface}")
        else:
            # Try to guess the MASTER_DEVICES dictionary
            if guess_used_ethernet_interface:
                # Try to guess the used Ethernet interfaces
                used_ethernet_interfaces = identify_ethernet_interfaces(logger)
                # Try to guess the MAC addresses of the used Ethernet interfaces
                guessed_master_devices = {}
                guessed_interface = None
                for i in used_ethernet_interfaces:
                    # Choose the first interface for which the MAC address is found
                    guessed_mac = get_mac_address(logger, i)
                    if guessed_mac is not None:
                        guessed_interface = i
                        guessed_master_devices["MASTER0_DEVICE"] = guessed_mac
                        break
            else:
                if used_ethernet_interfaces is None and MASTER_DEVICES is None and interactive is False:
                    logger.error(
                        "You must define either MASTER_DEVICES or used_ethernet_interfaces or interactive to True")
                    raise Exception(
                        "You must define either MASTER_DEVICES or used_ethernet_interfaces or interactive to True")

            if interactive:
                ok = "n"
                if guess_used_ethernet_interface:
                    # Ask the user to confirm the guessed values or to enter new values
                    hw_addr = get_hw_info(guessed_interface, logger)
                    hw_type = get_hw_type(guessed_interface, logger)
                    info = get_more_hw_info(hw_addr, hw_type, logger)
                    print(
                        f"The following Ethernet interface has been guessed:\n\t{guessed_interface}\n{info}")
                    ok = input(
                        "Do you want to use this Ethernet interface ? [Y/n] > ")
                    ok = ok.lower().strip()
                    if "y" != ok and "" != ok:
                        ok = "n"
                    else:
                        to_use_master_devices = guessed_master_devices
                while "n" == ok:
                    try:
                        to_use_master_devices = interactively_choose_master_devices(
                            logger)
                        ok = "y"
                    except Exception as e:
                        ok = input(
                            "Do you want to retry ? [Y/n] > ")
                        ok = ok.lower().strip()
                        if "y" != ok and "" != ok:
                            sys.exit(-1)
    logger.info(f"MASTER_DEVICES={to_use_master_devices}")
    to_use_device_modules = None
    if device_modules is not None:
        # Then the parameter superseeds all the others
        # Check if the values are correct
        wanted_device_modules = device_modules.split()
        for module in wanted_device_modules:
            if module not in known_device_modules:
                logger.error(f"Invalid value in device_modules: {module}")
                raise Exception("Invalid value in device_modules")
        to_use_device_modules = device_modules
    else:
        if interactive:
            # Ask the user to choose one of the known device modules
            choice_display = ""
            for i, module in enumerate(known_device_modules):
                choice_display += f"\n{i+1}: {module}\n"
            choice_recognized = False
            while not choice_recognized:
                user_choice = input(
                    f"Choose a set of known device modules (enter a list of number separated by ';'):\n{choice_display}? > ")
                try:
                    user_choice = [int(x) for x in user_choice.split(";")]
                    for c in user_choice:
                        if c <= 0 or c > len(known_device_modules):
                            print(f"Invalid choice: {c}")
                            raise ValueError
                    choice_recognized = True
                except ValueError:
                    pass
            if choice_recognized:
                to_use_device_modules = " ".join(
                    [known_device_modules[c-1] for c in user_choice])

    # Update the configuration file
    logger.info(f"Updating the configuration file {cfg_file}...")
    # Read the configuration file
    with open(cfg_file, "r") as f:
        lines = f.readlines()
    master_devices_written = False
    device_modules_written = False
    # Update the configuration file
    with open(cfg_file, "w") as f:
        for l in lines:
            # Find if the line starts with MASTER[0-9]+_DEVICE= regex
            if re.match(r"^MASTER[0-9]+_DEVICE=", l):
                if master_devices_written:
                    continue
                else:
                    if l.startswith("MASTER0_DEVICE"):
                        for k, v in to_use_master_devices.items():
                            f.write(f"{k}=\"{v}\"\n")
                        master_devices_written = True
            # Find if the line starts with DEVICE_MODULES=
            elif l.startswith("DEVICE_MODULES="):
                if device_modules_written:
                    continue
                else:
                    f.write(f"DEVICE_MODULES=\"{to_use_device_modules}\"\n")
                    device_modules_written = True
            else:
                f.write(l)


@typechecked
def def_source_dir() -> str:
    # Create the source directory name
    source_dir = f"{src_dest}-{git_branch}"
    # Check if the source directory is an absolute path
    if not os.path.isabs(src_dest):
        logger.error("The src_dest directory path must be an absolute path")
        raise Exception("The src_dest directory path must be an absolute path")
    return source_dir


@typechecked
def clone_sources(source_dir: str):
    # Create the source directory if it does not exist
    os.makedirs(source_dir)
    # Otherwise download the source code from the internet
    # fail if no network connection is available
    logger.info("Downloading source code...")
    try:
        subprocess.run(["git", "clone", git_project, source_dir],
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
        os.chdir(source_dir)
        subprocess.run(["git", "checkout", git_branch],
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Impossible to download the source code then checkout the branch {git_branch}: {e}")
        raise Exception(
            "Impossible to download the source code and checkout the correct branch")


@typechecked
def clone():
    source_dir = def_source_dir()
    clone_sources(source_dir)


@typechecked
def build_module():
    # Install the required dependencies
    # (if a network connection is available)
    logger.info("Installing dependencies...")
    try:
        result = subprocess.run(["apt-get", "update"],
                                check=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        logger.info(f"Impossible to run apt-get update: {e}")
    for d in dependencies:
        try:
            result = subprocess.run(["apt-get", "install", "-y", d],
                                    check=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            logger.info(f"Impossible to install {d}: {e}")

    # Create the source directory name
    source_dir = def_source_dir()
    # Check if the source directory exists and is up-to-date
    # (if a network connection is available)
    if os.path.exists(source_dir):
        # Update the source code
        logger.info("Updating source code...")
        os.chdir(source_dir)
        try:
            subprocess.run(["git", "pull"],
                           check=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            logger.info(f"Impossible to update the source code: {e}")
        # Checkout the correct branch
        try:
            subprocess.run(["git", "checkout", git_branch],
                           check=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            logger.error(f"Impossible to checkout the branch: {e}")
            raise Exception("Impossible to checkout the branch")
    else:
        # Otherwise download the source code from the internet
        # fail if no network connection is available
        clone_sources(source_dir)

    # Remove the files generated by a previous build
    logger.info("Cleaning previous generated files...")
    for file in installed_files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except Exception as e:
                logger.info(
                    f"Impossible to remove {file}: {e}. Maybe you need to run the script as root.")

    # Create the configure script
    logger.info("Creating configure script...")
    os.chdir(source_dir)
    try:
        subprocess.run(["./bootstrap"],
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        logger.error(f"Impossible to create the configure script: {e}")
        raise Exception("Impossible to create the configure script")

    # Configure the source code
    logger.info("Configuring source code...")
    os.chdir(source_dir)
    # Create the configure command
    configure_cmd = ["./configure"]
    for k, v in configure_options.items():
        if v["active"]:
            if v["value"] is not None:
                if v["default"] != v["value"]:
                    configure_cmd.append(f"{k}={v['value']}")
            else:
                configure_cmd.append(f"{v['value']}")
    for k, v in configure_switches.items():
        if v["active"]:
            if v["default"] != v["active_value"]:
                configure_cmd.append(v["active_value"])
        else:
            inactive_value = v.get("inactive_value", None)
            if inactive_value is not None:
                if v["default"] != inactive_value:
                    configure_cmd.append(v["inactive_value"])
    # Run the configure command
    try:
        cmd_joined = " ".join(configure_cmd)
        logger.info(f"Configure command: {cmd_joined}")
        subprocess.run(configure_cmd,
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        logger.error(f"Impossible to configure the source code: {e}")
        raise Exception("Impossible to configure the source code")
    #
    # Build the module
    logger.info("Building module...")
    try:
        subprocess.run(["make", "all", "modules"],
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        logger.error(f"Impossible to build the module: {e}")
        raise Exception("Impossible to build the module")


@typechecked
def install_module():
    # Install the module
    logger.info("Installing module...")
    try:
        subprocess.run(["make", "modules_install"],
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        logger.error(f"Impossible to install the module: {e}")
        raise Exception("Impossible to install the module")

    # Run depmod to update module dependencies
    logger.info("Running depmod...")
    try:
        subprocess.run(["depmod"],
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        logger.error(f"Impossible to run depmod: {e}")
        raise Exception("Impossible to run depmod")

    # Create symbolic links
    logger.info("Creating symbolic links...")
    if configure_options["--prefix"]["active"]:
        install_dir = configure_options["--prefix"]["value"]
    else:
        install_dir = configure_options["--prefix"]["default"]
    # Create install directory if it does not exist
    if not os.path.exists(install_dir):
        os.makedirs(install_dir)
    for l in links_to_create:
        try:
            os.symlink(l[0].format(install_path=install_dir), l[1])
        except FileExistsError as e:
            logger.error(f"Impossible to create the symbolic link {l}: {e}")
            raise Exception("Impossible to create the symbolic link")

    # Create sysconfig directory if it does not exist
    if not os.path.exists(cfg_path):
        os.makedirs(cfg_path)

    # Manage the configuration files
    logger.info("Manage the configuration file...")
    # Otherwise copy the configuration file
    for c in cfg_file_copy:
        # If a configuration file already exists do nothing
        if os.path.exists(c[1]):
            logger.info(f"Configuration file {c[1]} already exists")
        else:
            # Copy the configuration file
            try:
                shutil.copy(c[0].format(install_path=install_dir), c[1])
            except FileNotFoundError as e:
                logger.error(
                    f"Impossible to copy the configuration file {c}: {e}")
                raise Exception("Impossible to copy the configuration file")
            # Update the configuration file
            if cfg_path+"/ethercat" == c[1]:
                update_ethercat_config(c[1])

    # Create the udev rule file
    logger.info("Creating the udev rule file...")
    with open(udev_rule_file, "w") as f:
        f.write(udev_rule)


@typechecked
def create_logger(proj_name: str = "ethercat_igh_dkms", log_dir: str = "/var/log/ethercat_igh_dkms"):
    global logger
    # Create the log directory if it does not exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    # Keep only one log file
    keep_one_file_log_history(proj_name, log_dir)
    # Initialize the logger
    logger = init_logging(proj_name, log_dir)


@typechecked
def get_logger() -> Optional[Logger]:
    return logger


@typechecked
def set_configure_prefix(value: str):
    configure_options["--prefix"]["value"] = value


@typechecked
def set_src_install(value: str):
    global src_install
    src_install = value


@typechecked
def set_src_dest(value: str):
    global src_dest
    src_dest = os.path.join(src_install, value)


@typechecked
def modifyAndCreate(src: str, dst: str, dict: dict):
    try:
        currentFile = None
        with open(src) as fd:
            currentFile = fd.read()
        with open(dst, "w") as fd:
            content = currentFile % dict
            fd.write(content)
    except Exception as e:
        logger.error(
            f"Error {e} when reading file {src} and trying to write file {dst}.")
        raise e


@typechecked
def create_dkms_config():
    """
    Automatically create the DKMS configuration file, from the data
    gathered from the first build
    """
    sources_dir = def_source_dir()
    # Find the kernel modules inside build dir
    cmd = "find "+sources_dir+" -name '*.ko'"
    result = subprocess.run(
        cmd, shell=True, check=True, stdout=subprocess.PIPE)
    kernel_modules = result.stdout.decode().split("\n")
    # remove empty strings
    kernel_modules = [k for k in kernel_modules if "" != k]
    # Display built modules
    pretty_print = ""
    for k in kernel_modules:
        pretty_print = pretty_print + k + " ; "
    pretty_print = pretty_print[:-3]
    logger.info(f"Built modules: {pretty_print}")
    # Check that ec_master.ko is in the list
    # Check that in devices ec_xxxx.ko is in the list  of known device modules
    modules_info = []
    for k in kernel_modules:
        p_tot = Path(k)
        p_build = Path(sources_dir)
        rel_path = p_tot.relative_to(p_build)
        sp = k.split("/")
        modules_info.append(
            {
                "module_name": sp[-1].split(".")[0],
                "module_dest": rel_path
            }
        )
    dico = {}
    # Build the string for BUILT_MODULE_NAME and DEST_MODULE_LOCATION for dkms
    bmn = ""
    for i, m in enumerate(modules_info):
        module_name = m["module_name"]
        module_dest = m["module_dest"]
        bmn = bmn + f"BUILT_MODULE_NAME[{i}]=\"{module_name}\"\n"
        bmn = bmn + f"DEST_MODULE_LOCATION[{i}]=\"{module_dest}\"\n"
    dico["BUILT_and_DEST_MODULE_NAME"] = bmn
    # Get the absolute path of the current file
    proj_path = os.path.abspath(__file__)
    # Get the parent directory of the parent directory of the current file
    proj_path = os.path.dirname(os.path.dirname(proj_path))
    dico["PROJECT_LOCATION"] = proj_path
    # The DKMS configuration file will be written in the source directory
    dkms_cfg_file = os.path.join(sources_dir, "dkms.conf")
    template_cfg_file = os.path.join(proj_path, "dkms", "dkms.conf.template")
    modifyAndCreate(template_cfg_file, dkms_cfg_file, dico)
