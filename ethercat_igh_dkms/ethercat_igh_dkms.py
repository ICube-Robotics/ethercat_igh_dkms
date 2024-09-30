from io import BufferedReader
import os
import sys
import subprocess
import shutil
import logging
from logging import Logger
import time
from typing import Tuple
from typeguard import typechecked
import re
from pathlib import Path
import importlib
import json

from .parameters import *
from .get_mac import *
from .get_hw_info import *


###############################
# Global variables
###############################

# Get the current kernel version
kernel_version = subprocess.check_output(["uname", "-r"]).strip().decode()
project_dir = Path(os.path.abspath(__file__)).parent.parent
in_use_device_modules = set()
installed_files_tracker = {}
installed_files_tracker_name = "installed_files.json"
logger = None

###############################
# Utility Functions and classes
###############################


@typechecked
def record_file(file_path: str):
    global installed_files_tracker
    # Get the absolute path of the file
    file_path = os.path.abspath(file_path)
    if file_path not in installed_files_tracker:
        installed_files_tracker[file_path] = {
            "type": "file"
        }
    else:
        if installed_files_tracker[file_path]["type"] != "file":
            raise Exception(
                f"File {file_path} already recorded as a directory")


@typechecked
def record_directory(dir_path: str):
    global installed_files_tracker
    # Get the absolute path of the directory
    dir_path = os.path.abspath(dir_path)
    if dir_path not in installed_files_tracker:
        installed_files_tracker[dir_path] = {
            "type": "directory"
        }
    else:
        if installed_files_tracker[dir_path]["type"] != "directory":
            raise Exception(f"Directory {dir_path} already recorded as a file")


@typechecked
def save_installed_files():
    global installed_files_tracker
    save_file_path = os.path.join(project_dir, installed_files_tracker_name)
    with open(save_file_path, "w") as f:
        json.dump(installed_files_tracker, f, indent=2)


@typechecked
def load_installed_files():
    global installed_files_tracker
    save_file_path = os.path.join(project_dir, installed_files_tracker_name)
    if os.path.exists(save_file_path):
        with open(save_file_path, "r") as f:
            installed_files_tracker = json.load(f)


@typechecked
def clean_installed_files():
    """
    Clean the installed files and directories. All files and directories are concerned 
    except:
    - the directory of the project containing this script
    - the log directory: /var/log/ethercat_igh_dkms
    """
    global installed_files_tracker
    installed_files_tracker = {}
    load_installed_files()
    for k, v in installed_files_tracker.items():
        if v["type"] == "file":
            if os.path.exists(k):
                os.remove(k)
        elif v["type"] == "directory":
            if os.path.exists(k):
                shutil.rmtree(k)


@typechecked
def handle_subprocess_error(e: Exception, cmd: str, exit: bool = False, raise_exception: bool = False):
    res_out = e.stdout.decode() if e.stdout else "No stdout"
    res_err = e.stderr.decode() if e.stderr else "No stderr"
    imsg = f"ERROR: {cmd}. Details: {e}, {res_out} {res_err}"
    logger.error(imsg)
    if exit:
        print(imsg)
        sys.exit(-1)
    if raise_exception:
        raise Exception(cmd)


@typechecked
def keep_one_file_log_history(logger_name: str, log_file_path: str):
    # Keep only one log file
    log_files = [f for f in os.listdir(log_file_path) if f.endswith(".log")]
    # find all log_files containing logger_name
    log_files = [f for f in log_files if logger_name in f]
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


class FlushFileHandler(logging.FileHandler):
    """
    A handler class which writes logging records flushing after each record.
    """

    def emit(self, record):
        super().emit(record)
        self.flush()  # Ensure flushing happens right after emit


@typechecked
def init_logging(logger_name: str, log_file_path: str) -> Logger:
    # Setup logging service
    logger = Logger.manager.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = FlushFileHandler(os.path.join(log_file_path, logger_name + ".log"))
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
                        to_use_master_devices = guessed_master_devices
                        break
            else:
                if used_ethernet_interfaces is None and MASTER_DEVICES is None and interactive is False:
                    logger.error(
                        "You must define either MASTER_DEVICES or used_ethernet_interfaces or interactive to True")
                    raise Exception(
                        "You must define either MASTER_DEVICES or used_ethernet_interfaces or interactive to True")

            if interactive:
                to_use_master_devices = None
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
    # Store the set of device modules in use
    global in_use_device_modules
    in_use_device_modules = set(to_use_device_modules.split())


@typechecked
def get_kernel_version(kernel_sources: str) -> str:
    """
    Get the kernel version from the kernel sources path
    """
    # get the last directory of the path
    dir = os.path.basename(kernel_sources)
    # Check if the directory name is a valid kernel version
    start = "linux-headers-"
    if start != dir[:len(start)]:
        raise Exception(f"Invalid kernel sources directory name: {dir}")
    return dir[len(start):]


@typechecked
def def_source_dir(kernel_sources: Optional[str] = None) -> str:
    if None != kernel_sources:
        kernel_version = get_kernel_version(kernel_sources)
    # Create the source directory name
    source_dir = f"{src_build}-{git_branch}-{kernel_version}"
    # Check if the source directory is an absolute path
    if not os.path.isabs(src_build):
        logger.error("The src_build directory path must be an absolute path")
        raise Exception(
            "The src_build directory path must be an absolute path")
    return source_dir


@typechecked
def clone_sources(source_dir: str):
    parent = Path(source_dir).parent
    os.makedirs(parent, exist_ok=True)
    # Otherwise download the source code from the internet
    # fails if no network connection is available
    logger.info("Downloading source code...")
    try:
        cmd = ["git", "clone", git_project, source_dir]
        exec_cmd(cmd)
        os.chdir(source_dir)
        cmd = ["git", "checkout", git_branch]
        exec_cmd(cmd)
        os.chdir(project_dir)
    except subprocess.CalledProcessError as e:
        imsg = f"Impossible to download the source code then checkout the branch {git_branch}"
        handle_subprocess_error(e, imsg, exit=False, raise_exception=True)


@typechecked
def clone():
    source_dir = def_source_dir()
    clone_sources(source_dir)


@typechecked
def check_secure_boot_state():
    logger.info("Checking the secure boot state...")
    try:
        cmd = ["mokutil", "--sb-state"]
        _, result = exec_cmd(cmd)
    except subprocess.CalledProcessError as e:
        imsg = "Impossible to check the secure boot state"
        handle_subprocess_error(e, imsg, exit=False, raise_exception=True)
    output = result
    if "SecureBoot enabled" in output:
        imsg = "SecureBoot is enabled. You must disable it to install igh EtherCAT master kernel modules and tools. Following is a summary of the procedure:\n\t1. Reboot your computer and enter the BIOS setup\n\t2. Find the Secure Boot option and disable it\n\t3. Save the changes and reboot your computer\n"
        logger.error(imsg)
        raise Exception(imsg)
    elif "SecureBoot disabled" in output:
        logger.info("SecureBoot is disabled.")
    else:
        imsg = "Impossible to check the secure boot state"
        logger.error(imsg)
        raise Exception(imsg)


@typechecked
def append_and_print(res: str, stdio: BufferedReader) -> str:
    # print(f"Type of stdio: {type(stdio)}")
    if None == stdio:
        return res
    text = stdio.read1().decode("utf-8")
    text1 = text.strip()
    if "" != text1:
        res += text
        print(text1, flush=True)
    return res


@typechecked
def exec_cmd(cmd: list, timeout: Optional[float] = None) -> Tuple[int, str]:
    str_cmd = " ".join(cmd)
    print(f"Executing command: «{str_cmd}»")
    res = ""
    with subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    ) as process:
        if timeout is not None:
            start_time = time.monotonic()
        while True:
            res = append_and_print(res, process.stdout)
            c = process.poll()
            if c is not None:
                return c, res
            if timeout is not None:
                if time.monotonic() - start_time > timeout:
                    res += "\nTimeout reached"
                    process.kill()
                    return -1, res


@typechecked
def exec_cmd_stderr(cmd: list, timeout: Optional[float] = None) -> Tuple[int, str, str]:
    str_cmd = " ".join(cmd)
    print(f"Executing command: «{str_cmd}»")
    res = ""
    std_err = ""
    with subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    ) as process:
        if timeout is not None:
            start_time = time.monotonic()
        while True:
            res = append_and_print(res, process.stdout)
            std_err = append_and_print(std_err, process.stderr)
            c = process.poll()
            if c is not None:
                std_err = append_and_print(std_err, process.stderr)
                return c, res, std_err
            if timeout is not None:
                if time.monotonic() - start_time > timeout:
                    res += "\nTimeout reached"
                    process.kill()
                    return -1, res


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
def set_src_kernel_modules(value: str):
    global src_kernel_modules
    src_kernel_modules = value


@typechecked
def set_src_build(value: str):
    global src_build
    src_build = os.path.join(src_kernel_modules, value)


@typechecked
def set_interactive(value: bool):
    global interactive
    interactive = value


@typechecked
def get_kernel() -> str:
    global kernel_version
    kernel_version = subprocess.check_output(["uname", "-r"]).strip().decode()
    return kernel_version


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
def get_pkg_name() -> str:
    return "ethercat"


@typechecked
def get_version() -> str:
    return git_branch


@typechecked
def get_dkms_name() -> str:
    return f"ethercat/{git_branch}"


@typechecked
def find_built_kernel_modules(sources_dir: str) -> list[str]:
    # Find the kernel modules inside build dir
    cmd = "find "+sources_dir+" -name '*.ko'"
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        imsg = "Impossible to find the kernel modules"
        handle_subprocess_error(e, imsg, exit=True, raise_exception=False)
    kernel_modules = result.stdout.decode().split("\n")
    # remove empty strings
    kernel_modules = [k for k in kernel_modules if "" != k]
    return kernel_modules


@typechecked
def kernel_modules_file_names(built_kernel_modules: list[str]) -> list[str]:
    return [Path(k).name for k in built_kernel_modules]


@typechecked
def kernel_modules_standard_relative_path(sources_dir: str, built_kernel_modules: list[str]) -> list[str]:
    root = Path(sources_dir)
    return [str(Path(k).relative_to(root)) for k in built_kernel_modules]


@typechecked
def kernel_modules_paths(sources_dir: str) -> list[str]:
    built_modules = find_built_kernel_modules(sources_dir)
    rel_paths = kernel_modules_standard_relative_path(
        sources_dir, built_modules)
    standard_kernel_modules_path = "/lib/modules/" + kernel_version + "/ethercat/"
    return [standard_kernel_modules_path + p for p in rel_paths]


@typechecked
def create_dkms_config():
    """
    Automatically create the DKMS configuration file, from the data
    gathered from the first build
    """
    sources_dir = def_source_dir()
    # Find the kernel modules inside build dir
    kernel_modules = find_built_kernel_modules(sources_dir)
    # Display built modules
    pretty_print = ""
    for k in kernel_modules:
        pretty_print = pretty_print + k + " ; "
    pretty_print = pretty_print[:-3]
    logger.info(f"Built modules: {pretty_print}")
    modules_info = []
    install_mod_dir = None
    # Get the installation directory of the kernel modules
    opt = configure_options["--with-module-dir"]
    if opt["active"]:
        install_mod_dir = opt["value"]
    else:
        install_mod_dir = opt["default"]
    for k in kernel_modules:
        p_tot = Path(k)
        p_build = Path(sources_dir)
        rel_path = p_tot.relative_to(p_build).parent
        # get only the directory name
        dest_path = Path(install_mod_dir).joinpath(rel_path)
        sp = k.split("/")
        modules_info.append(
            {
                "module_name": sp[-1].split(".")[0],
                "module_built": rel_path,
                "module_dest": dest_path
            }
        )
    dico = {}
    dico["POETRY_BINARY_DIR"] = poetry_binary_dir
    # Build the string for BUILT_MODULE_NAME and DEST_MODULE_LOCATION for dkms
    bmn = ""
    for i, m in enumerate(modules_info):
        module_name = m["module_name"]
        module_dest = str(m["module_dest"])
        module_built = str(m["module_built"])
        bmn = bmn + f"BUILT_MODULE_NAME[{i}]=\"{module_name}\"\n"
        bmn = bmn + f"BUILT_MODULE_LOCATION[{i}]=\"{module_built}\"\n"
        if "/" != module_dest[0]:
            module_dest = "/" + module_dest
        bmn = bmn + f"DEST_MODULE_LOCATION[{i}]=\"{module_dest}\"\n"
    dico["MODULE_NAMES_and_BUILT_and_DEST_LOCATIONS"] = bmn[:-1]
    # Get the absolute path of the current file
    proj_path = os.path.abspath(__file__)
    # Get the parent directory of the parent directory of the current file
    proj_path = os.path.dirname(os.path.dirname(proj_path))
    dico["PROJECT_LOCATION"] = proj_path
    # The DKMS configuration file will be written in the source directory
    dkms_cfg_file = os.path.join(sources_dir, "dkms.conf")
    template_cfg_file = os.path.join(proj_path, "dkms", "dkms.conf.template")
    modifyAndCreate(template_cfg_file, dkms_cfg_file, dico)
    #
    # Create the post_install script for dkms
    dkms_post_install_file = os.path.join(sources_dir, "dkms.post_install.sh")
    template_post_install_file = os.path.join(
        proj_path, "dkms", "dkms.post_install.template")
    modifyAndCreate(template_post_install_file, dkms_post_install_file, dico)
    # make the post_install script executable
    os.chmod(dkms_post_install_file, 0o755)


@typechecked
def get_kernel_module_names() -> list[str]:
    sources_dir = def_source_dir()
    # Find the kernel modules inside build dir
    cmd = "find "+sources_dir+" -name '*.ko'"
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        imsg = "Impossible to find the kernel modules"
        handle_subprocess_error(e, imsg, exit=True, raise_exception=False)
    kernel_modules = result.stdout.decode().split("\n")
    # remove empty strings
    kernel_modules = [k for k in kernel_modules if "" != k]
    # Check that ec_master.ko is in the list
    master_found = False
    # Check that in devices ec_xxxx.ko is in the list  of known device modules
    all_devices_found = []
    for k in kernel_modules:
        sp = k.split("/")
        dir = sp[-2]
        mod = sp[-1].split(".")[0]
        if "master" == dir:
            if "ec_master" == mod:
                master_found = True
        elif "devices" == dir:
            mod = mod[3:]  # remove the ec_ prefix
            all_devices_found.append(mod)
    return ["ec_" + x for x in all_devices_found].append("ec_master")


@typechecked
def reload_parameters():
    """
    Reload the parameters from the parameters.py file
    """
    # Reload the parameters
    if 'parameters' in sys.modules:
        # Reload the module if it's already loaded
        importlib.reload(sys.modules['parameters'])
    else:
        # Otherwise, import it for the first time
        from . import parameters

    # Dynamically import all elements
    globals().update(vars(sys.modules['parameters']))

    # Get the current kernel version
    global kernel_version
    kernel_version = subprocess.check_output(["uname", "-r"]).strip().decode()


@typechecked
def do_systemd_autoinstall():
    return systemd_autoinstall


###############################
# Main functions
###############################


@typechecked
def build_module(do_install_dependencies: bool = True, check_secure_boot: bool = True, kernel_sources: Optional[str] = None):
    if do_install_dependencies:
        # Install the required dependencies
        # (if a network connection is available)
        logger.info("Installing dependencies...")
        try:
            cmd = ["apt-get", "update"]
            _, result = exec_cmd(cmd)
        except subprocess.CalledProcessError as e:
            imsg = "Impossible to run apt-get update"
            handle_subprocess_error(e, imsg, exit=False, raise_exception=False)
        for d in dependencies:
            try:
                cmd = ["apt-get", "install", "-y", d]
                _, result = exec_cmd(cmd)
            except subprocess.CalledProcessError as e:
                imsg = f"Impossible to install {d}"
                handle_subprocess_error(
                    e, imsg, exit=False, raise_exception=False)
    if check_secure_boot:
        # Check the secure boot state
        check_secure_boot_state()

    # Create the source directory name
    source_dir = def_source_dir(kernel_sources)
    record_directory(source_dir)
    # Check if the source directory exists and is up-to-date
    # (if a network connection is available)
    got_sources = False
    if os.path.exists(source_dir):
        # Check if the source directory contains the correct git repository
        os.chdir(source_dir)
        correct_git_repo = False
        try:
            cmd = ["git", "remote", "-v"]
            _, result = exec_cmd(cmd)
            if git_project in result:
                correct_git_repo = True
        except subprocess.CalledProcessError as e:
            imsg = "Impossible to check the git repository"
            handle_subprocess_error(e, imsg, exit=False, raise_exception=False)
            correct_git_repo = False
        if correct_git_repo:
            # Update the source code
            logger.info("Updating source code...")
            try:
                try:
                    cmd = ["git", "pull"]
                    _, result = exec_cmd(cmd)
                except subprocess.CalledProcessError as e:
                    imsg = "Impossible to update the source code"
                    handle_subprocess_error(
                        e, imsg, exit=False, raise_exception=False)
                # Check the current branch
                try:
                    cmd = ["git", "branch", "--show-current"]
                    _, result = exec_cmd(cmd)
                    if git_branch.strip() == result.strip():
                        got_sources = True
                        imsg = f"Source code is on the correct branch {git_branch}"
                        logger.info(imsg)
                    else:
                        # Stash the changes
                        try:
                            cmd = ["git", "stash"]
                            _, result = exec_cmd(cmd)
                        except subprocess.CalledProcessError as e:
                            imsg = "Impossible to stash the changes"
                            handle_subprocess_error(
                                e, imsg, exit=False, raise_exception=True)
                        # Checkout the correct branch
                        try:
                            cmd = ["git", "checkout", git_branch]
                            _, result = exec_cmd(cmd)
                        except subprocess.CalledProcessError as e:
                            imsg = f"Impossible to checkout the branch {git_branch}"
                            handle_subprocess_error(
                                e, imsg, exit=False, raise_exception=True)
                except subprocess.CalledProcessError as e:
                    imsg = "Impossible to check the current branch"
                    handle_subprocess_error(
                        e, imsg, exit=False, raise_exception=True)
                got_sources = True
            except Exception as e:
                imsg = f"Impossible to validate that a proper version of the source code is available: {e}"
                logger.error(imsg)
                got_sources = False

    if not got_sources:
        # Clean the mess and remove the source directory if it exists
        if os.path.exists(source_dir):
            shutil.rmtree(source_dir)
        # Otherwise download the source code from the internet
        # fail if no network connection is available
        clone_sources(source_dir)
        got_sources = True

    # Clean the source directory
    logger.info("Cleaning source directory...")
    os.chdir(source_dir)
    try:
        cmd = ["make", "clean"]
        exec_cmd(cmd)
    except subprocess.CalledProcessError as e:
        imsg = "Impossible to clean the source directory"
        handle_subprocess_error(e, imsg, exit=True, raise_exception=True)

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
        cmd = ["./bootstrap"]
        _, result = exec_cmd(cmd)
    except subprocess.CalledProcessError as e:
        imsg = "Impossible to run the bootstrap script"
        handle_subprocess_error(e, imsg, exit=False, raise_exception=True)
    if "You should run autoupdate" in result:
        try:
            cmd = ["autoupdate"]
            _, result = exec_cmd(cmd)
        except subprocess.CalledProcessError as e:
            imsg = "Impossible to run the autoupdate script"
            handle_subprocess_error(e, imsg, exit=True, raise_exception=True)
        try:
            cmd = ["./bootstrap"]
            exec_cmd(cmd)
        except subprocess.CalledProcessError as e:
            imsg = "Impossible to run the bootstrap script"
            handle_subprocess_error(e, imsg, exit=True, raise_exception=True)
    os.chdir(project_dir)

    # Update the configuration file with the kernel source directory info
    if None != kernel_sources:
        configure_options["--with-linux-dir"]["active"] = True
        configure_options["--with-linux-dir"]["value"] = kernel_sources

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
        exec_cmd(configure_cmd)
    except subprocess.CalledProcessError as e:
        imsg = "Impossible to configure the source code"
        handle_subprocess_error(e, imsg, exit=False, raise_exception=True)
    #
    # Build the module
    logger.info("Building module...")
    try:
        cmd = ["make", "all", "modules"]
        exec_cmd(cmd)
    except subprocess.CalledProcessError as e:
        imsg = "Impossible to build the module"
        handle_subprocess_error(e, imsg, exit=False, raise_exception=True)
    # Get the built kernel modules and record their standard installation path
    built_modules = kernel_modules_paths(source_dir)
    for m in built_modules:
        record_file(m)
    os.chdir(project_dir)


@typechecked
def install_module(kernel_sources: Optional[str] = None):
    # Install the modules
    logger.info("Installing module...")
    source_dir = def_source_dir(kernel_sources)
    os.chdir(source_dir)
    try:
        cmd = ["make", "modules_install"]
        exec_cmd(cmd)
    except subprocess.CalledProcessError as e:
        imsg = "Impossible to install the module"
        handle_subprocess_error(e, imsg, exit=False, raise_exception=True)

    # Run depmod to update module dependencies
    logger.info("Running depmod...")
    try:
        subprocess.run(["depmod"],
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        imsg = "Impossible to run depmod"
        handle_subprocess_error(e, imsg, exit=False, raise_exception=True)


@typechecked
def check_master_starts() -> bool:
    # Check if the master starts
    logger.info("Checking if the master starts...")
    try:
        cmd = ["/etc/init.d/ethercat", "start"]
        _, output = exec_cmd(cmd)
    except subprocess.CalledProcessError as e:
        imsg = "Impossible to start the master"
        handle_subprocess_error(e, imsg, exit=False, raise_exception=False)
        return False
    # Chech that the standard output contains "Starting EtherCAT Master x.x.x done"
    check_output = output.lower()
    if "Starting EtherCAT master".lower() not in check_output:
        imsg = f"The master did not start: {output}"
        logger.error(imsg)
        return False
    if "done" not in check_output:
        imsg = f"The master did not start: {output}"
        logger.error(imsg)
        return False
    # Stop the master
    try:
        cmd = ["/etc/init.d/ethercat", "stop"]
        _, output = exec_cmd(cmd)
    except subprocess.CalledProcessError as e:
        imsg = "Impossible to stop the master"
        handle_subprocess_error(e, imsg, exit=False, raise_exception=False)
        return False
    return True


@typechecked
def post_install(override_config: bool = False, kernel_sources: Optional[str] = None):
    logger.info("Post install tasks...")
    source_dir = def_source_dir(kernel_sources)
    os.chdir(source_dir)
    # Run depmod to update module dependencies
    logger.info("Running depmod...")
    try:
        cmd = ["depmod", "-a"]
        _, result = exec_cmd(cmd)
    except subprocess.CalledProcessError as e:
        str_cmd = " ".join(cmd)
        imsg = f"Impossible to run {str_cmd}"
        handle_subprocess_error(e, imsg, exit=True, raise_exception=False)
    # Install tools
    try:
        subprocess.run(["make", "install"],
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        imsg = "Impossible to install the ethercat tools"
        handle_subprocess_error(e, imsg, exit=False, raise_exception=True)
    # Remove symbolic links if they exist
    for l in links_to_create:
        if os.path.exists(l[1]):
            try:
                os.remove(l[1])
            except Exception as e:
                logger.error(
                    f"Impossible to remove the symbolic link {l[1]}: {e}")
                raise Exception("Impossible to remove the symbolic link")

    # Create symbolic links
    logger.info("Creating symbolic links...")
    if configure_options["--prefix"]["active"]:
        install_dir = configure_options["--prefix"]["value"]
    else:
        install_dir = configure_options["--prefix"]["default"]
    # Create install directory if it does not exist
    if not os.path.exists(install_dir):
        os.makedirs(install_dir)
    record_directory(install_dir)
    for l in links_to_create:
        try:
            # Check that links_to_create contains couple of strings
            if not isinstance(l, tuple) or not isinstance(l[0], str) or not isinstance(l[1], str):
                imsg = "links_to_create must contain couples of strings"
                logger.error(imsg)
                raise Exception(imsg)
            link = l[0].format(install_path=install_dir)
            logger.info(f"Creating symbolic link {l[1]} -> {link}")
            os.symlink(link, l[1])
            record_file(l[1])
        except Exception as e:
            logger.error(
                f"Impossible to create the symbolic link: {e}")
            raise Exception("Impossible to create the symbolic link")
    #
    # Create sysconfig directory if it does not exist
    if not os.path.exists(cfg_path):
        os.makedirs(cfg_path)
    #
    # Manage the configuration files
    logger.info("Manage the configuration file...")
    # Otherwise copy the configuration file
    for c in cfg_file_copy:
        record_file(c[1])
        # If a configuration file already exists do nothing
        if os.path.exists(c[1]) and not override_config:
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
    #
    # Create the udev rule file
    logger.info("Creating the udev rule file...")
    record_file(udev_rule_file)
    with open(udev_rule_file, "w") as f:
        f.write(udev_rule)
    # Reload the udev rules
    logger.info("Reloading the udev rules...")
    try:
        subprocess.run(["udevadm", "control", "--reload-rules"],
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        imsg = "Impossible to reload the udev rules"
        handle_subprocess_error(e, imsg, exit=False, raise_exception=True)
    # Check that the master starts
    if not check_master_starts():
        logger.error("The master did not start")
        raise Exception("The master did not start")
    else:
        logger.info("Success! The EtherCAT master starts correctly")
    # Post install is finished with success
    os.chdir(project_dir)
    logger.info("Success: post install finished")
