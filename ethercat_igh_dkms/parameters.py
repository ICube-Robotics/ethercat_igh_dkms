# Description: Parameters for the ethercat_igh_dkms project.
# ===========================================================

# The path to the poetry binary, it should stay on one line
poetry_binary_dir = "/usr/local/bin"
# f"{src_build}-{git_branch}" is where to compile the sources of the EtherCAT master
src_kernel_modules = "/usr/src"
src_build = f"{src_kernel_modules}/ethercat"
git_project = "https://gitlab.com/etherlab.org/ethercat.git"
git_branch = "stable-1.6"
# Automatically check at each boot if the EtherCAT master modules are available for the current kernel and install them if necessary.
systemd_autoinstall = True
# Guessing the Ethernet interface used for EtherCAT can work only in the
# case of a single Ethernet interface. If you have multiple Ethernet interfaces
# or the automatic guessing does not work, set the value to False.
guess_used_ethernet_interface = True
interactive = True
# Uncomment the lines starting with «used_ethernet_interfaces» and set
# the correct values if you do not want to use the automatic guess mode
# and/or the interactive mode and you know the names of the Ethernet
# interfaces.
used_ethernet_interfaces = None
"""
used_ethernet_interfaces = ["eth0"]
"""
# Uncomment the lines starting with «MASTER_DEVICES =» and set the correct value
# if you do not want to use the automatic guess mode and/or the interactive mode.
MASTER_DEVICES = None
""" 
MASTER_DEVICES = {
    "MASTER0_DEVICE" : "ff:ff:ff:ff:ff:ff"  # mac address
    }
"""
# Separate multiple drivers with spaces.
device_modules = "generic"
known_device_modules = [
    "generic", "8139too", "e100", "e1000", "e1000e", "r8169", "igb", "ccat"
]

project_dependencies = ["python3.10-full", "python3-poetry"]
dkms_dependencies = ["dkms"]
igh_ethercat_dependencies = ["git", "autoconf", "libtool",
                             "pkg-config", "make", "build-essential", "net-tools"]
test_dependencies = ["mokutil"]
dependencies = dkms_dependencies + igh_ethercat_dependencies + test_dependencies

installed_files = ["/usr/bin/ethercat", "/etc/init.d/ethercat"]
links_to_create = [
    ("{install_path}/bin/ethercat", "/usr/bin/ethercat"),
    ("{install_path}/etc/init.d/ethercat", "/etc/init.d/ethercat")
]
cfg_path = "/etc/sysconfig"
cfg_file_copy = [
    ("{install_path}"+cfg_path+"/ethercat", cfg_path+"/ethercat")
]
udev_rule_file = "/etc/udev/rules.d/99-ethercat.rules"
udev_rule = 'KERNEL=="EtherCAT[0-9]*", MODE="0666"'
configure_options = {
    "--prefix": {
        "active": True,
        "value": "/usr/local/etherlab",
        "doc": "Installation prefix",
        "default": "/opt/etherlab"
    },
    "--with-linux-dir": {
        "active": False,
        "value": None,
        "doc": "Linux kernel source directory. Default use running kernel.",
        "default": "/lib/modules/$(uname -r)/build"
    },
    "--with-module-dir": {
        "active": True,
        "value": "updates/ethercat",
        "doc": "Subdirectory in the kernel module tree, where the EtherCAT kernel modules shall be installed.",
        "default": "ethercat"
    },
    "--with-devices": {
        "active": False,
        "value": "1",
        "doc": "Number of Ethernet devices for redundant operation. Use more than 1 to enable redundancy.",
        "default": "1"
    },
    "--with-systemdsystemunitdir": {
        "active": False,
        "value": None,
        "doc": "Systemd unit directory, default is auto. Use 'no' to disable service file installation.",
        "default": "auto"
    },
    "--with-rtai-dir": {
        "active": False,
        "value": None,
        "doc": "Directory of the RTAI installation (for RTAI examples and RTDM interface) for real-time support.",
        "default": "/usr/rtai"
    },
    "--with-xenomai-dir": {
        "active": False,
        "value": None,
        "doc": "Directory of the Xenomai installation (for Xenomai examples and RTDM interface) for real-time support.",
        "default": "/usr/xenomai"
    },
}

configure_switches = {
    "generic": {
        "active": True,
        "active_value": "--enable-generic",
        "inactive_value": "--disable-generic",
        "doc": "Build the generic Ethernet driver",
        "default": "--enable-generic"
    },
    "8139too": {
        "active": False,
        "active_value": "--enable-8139too",
        "inactive_value": "--disable-8139too",
        "doc": "Build the 8139too driver.",
        "default": "--enable-8139too"
    },
    "8139too-kernel": {
        "active": False,
        "active_value": "--with-8139too-kernel",
        "inactive_value": None,
        "doc": "8139too kernel version (optional).",
        "default": None
    },
    "e100": {
        "active": False,
        "active_value": "--enable-e100",
        "inactive_value": "--disable-e100",
        "doc": "Build the e100 driver.",
        "default": "--disable-e100"
    },
    "--with-e100-kernel": {
        "active": False,
        "active_value": "--with-e100-kernel",
        "inactive_value": None,
        "doc": "e100 kernel version (optional).",
        "default": None
    },
    "e1000": {
        "active": False,
        "active_value": "--enable-e1000",
        "inactive_value": "--disable-e1000",
        "doc": "Enable the e1000 driver.",
        "default": "--disable-e1000"
    },
    "--with-e1000-kernel": {
        "active": False,
        "active_value": "--with-e1000-kernel",
        "inactive_value": None,
        "doc": "e1000 kernel version (optional).",
        "default": None
    },
    "e1000e": {
        "active": False,
        "active_value": "--enable-e1000e",
        "inactive_value": "--disable-e1000e",
        "doc": "Enable the e1000e driver.",
        "default": "--disable-e1000e"
    },
    "--with-e1000e-kernel": {
        "active": False,
        "active_value": "--with-e1000e-kernel",
        "inactive_value": None,
        "doc": "e1000e kernel version (optional).",
        "default": None
    },
    "r8169": {
        "active": False,
        "active_value": "--enable-r8169",
        "inactive_value": "--disable-r8169",
        "doc": "Enable the r8169 driver.",
        "default": "--disable-r8169"
    },
    "--with-r8169-kernel": {
        "active": False,
        "active_value": "--with-r8169-kernel",
        "inactive_value": None,
        "doc": "r8169 kernel version (optional).",
        "default": None
    },
    "igb": {
        "active": False,
        "active_value": "--enable-igb",
        "inactive_value": "--disable-igb",
        "doc": "Enable the igb driver.",
        "default": "--disable-igb"
    },
    "--with-igb-kernel": {
        "active": False,
        "active_value": "--with-igb-kernel",
        "inactive_value": None,
        "doc": "igb kernel version (optional).",
        "default": None
    },
    "ccat": {
        "active": False,
        "active_value": "--enable-ccat",
        "inactive_value": "--disable-ccat",
        "doc": "Enable the CCAT driver (independent of kernel version).",
        "default": "--disable-ccat"
    },
    "kernel": {
        "active": True,
        "active_value": "--enable-kernel",
        "inactive_value": "--disable-kernel",
        "doc": "Build the master kernel modules.",
        "default": "--enable-kernel"
    },
    "rtdm": {
        "active": False,
        "active_value": "--enable-rtdm",
        "inactive_value": "--disable-rtdm",
        "doc": "Create the RTDM interface (RTAI or Xenomai directory needed).",
        "default": "--disable-rtdm"
    },
    "debug-if": {
        "active": False,
        "active_value": "--enable-debug-if",
        "inactive_value": "--disable-debug-if",
        "doc": "Create a debug interface for each master.",
        "default": "--disable-debug-if"
    },
    "debug-ring": {
        "active": False,
        "active_value": "--enable-debug-ring",
        "inactive_value": "--disable-debug-ring",
        "doc": "Create a debug ring to record frames.",
        "default": "--disable-debug-ring"
    },
    "eoe": {
        "active": False,
        "active_value": "--enable-eoe",
        "inactive_value": "--disable-eoe",
        "doc": "Enable Ethernet over EtherCAT (EoE) support.",
        "default": "--enable-eoe"
    },
    "cycles": {
        "active": False,
        "active_value": "--enable-cycles",
        "inactive_value": "--disable-cycles",
        "doc": "Use CPU timestamp counter for finer timing calculation (Intel architecture).",
        "default": "--disable-cycles"
    },
    "hrtimer": {
        "active": False,
        "active_value": "--enable-hrtimer",
        "inactive_value": "--disable-hrtimer",
        "doc": "Use high-resolution timer to let the master state machine sleep between sending frames.",
        "default": "--disable-hrtimer"
    },
    "regalias": {
        "active": False,
        "active_value": "--enable-regalias",
        "inactive_value": "--disable-regalias",
        "doc": "Read alias address from register.",
        "default": "--disable-regalias"
    },
    "tool": {
        "active": True,
        "active_value": "--enable-tool",
        "inactive_value": "--disable-tool",
        "doc": "Build the command-line tool 'ethercat'.",
        "default": "--enable-tool"
    },
    "userlib": {
        "active": True,
        "active_value": "--enable-userlib",
        "inactive_value": "--disable-userlib",
        "doc": "Build the userspace library.",
        "default": "--enable-userlib"
    },
    "tty": {
        "active": False,
        "active_value": "--enable-tty",
        "inactive_value": "--disable-tty",
        "doc": "Build the TTY driver.",
        "default": "--disable-tty"
    },
    "wildcards": {
        "active": False,
        "active_value": "--enable-wildcards",
        "inactive_value": "--disable-wildcards",
        "doc": "Enable 0xffffffff to be used as wildcards for vendor ID and product code.",
        "default": "--disable-wildcards"
    },
    "sii-assign": {
        "active": False,
        "active_value": "--enable-sii-assign",
        "inactive_value": "--disable-sii-assign",
        "doc": "Enable assigning SII access to the PDI layer during slave configuration.",
        "default": "--disable-sii-assign"
    },
    "rt-syslog": {
        "active": True,
        "active_value": "--enable-rt-syslog",
        "inactive_value": "--disable-rt-syslog",
        "doc": "Enable syslog statements in real-time context.",
        "default": "--enable-rt-syslog"
    }
}
