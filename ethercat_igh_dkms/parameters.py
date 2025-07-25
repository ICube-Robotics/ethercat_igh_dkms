# Description: Parameters for the ethercat_igh_dkms project.
# ===========================================================

# The path to the poetry binary, it should stay on one line
poetry_binary_dir = "/usr/local/bin"
# f"{src_build}-{git_branch}" is where to compile the sources of the EtherCAT master
src_kernel_modules = "/usr/src"
src_build = f"{src_kernel_modules}/ethercat"
git_project = "https://gitlab.com/etherlab.org/ethercat.git"
git_branch = "stable-1.6"
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
## To know which driver is supported for a specific igh version and linux kernel see:
##  version 1.6: https://docs.etherlab.org/ethercat/1.6/doxygen/devicedrivers.html
##  version 1.5: https://docs.etherlab.org/ethercat/1.5/doxygen/devicedrivers.html
device_modules = "generic"
## If you add a new known module, do not forget to also add the corresponding 
## configuration options in the variable 'configure_switches' at the end of the file
## If a kernel version may be specified for a module, the configuration option name must 
## take the form : 'module_name-kernel-version'
known_device_modules = [
    "generic", "8139too", "bcmgenet", "dwmac-intel", "e100", "e1000", "e1000e", "r8169", "igb", "igc", "stmmac-pci", "ccat"
]

project_dependencies = ["python3.10-full"]
igh_ethercat_dependencies = ["git", "autoconf", "libtool",
                             "pkg-config", "make", "build-essential", "net-tools", "linux-headers-%(kernel_version)s"]
test_dependencies = ["mokutil"]
dependencies = igh_ethercat_dependencies + test_dependencies

installed_files = ["/usr/bin/ethercat", "/etc/init.d/ethercat"]
links_to_create = [
    ("{install_path}/bin/ethercat", "/usr/bin/ethercat"),
    ("{install_path}/etc/init.d/ethercat", "/etc/init.d/ethercat")
]

cfg_path = "/etc/sysconfig"
cfg_project_path = "{install_path}" + cfg_path + "/ethercat"
cfg_file_copy = [
    (cfg_project_path, cfg_path+"/ethercat")
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
        "active": False,
        "value": None,
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
        "inactive_value": None,
        "doc": "Build the generic Ethernet driver",
        "default": "--enable-generic"
    },
    "8139too": {
        "active": False,
        "active_value": "--enable-8139too",
        "inactive_value": None,
        "doc": "Build the 8139too driver.",
        "default": None
    },
    "8139too-kernel-version": {
        "active": False,
        "active_value": "--with-8139too-kernel",
        "inactive_value": None,
        "doc": "8139too kernel version (optional).",
        "default": None
    },
    "bcmgenet": {
        "active": False,
        "active_value": "--enable-bcmgenet",
        "inactive_value": None,
        "doc": "Build the bcmgenet driver.",
        "default": None
    }, 
    "bcmgenet-kernel-version": {
        "active": False,
        "active_value": "--with-bcmgenet-kernel",
        "inactive_value": None,
        "doc": "bcmgenet kernel version (optional).",
        "default": None
    },
    "dwmac-intel": {
        "active": False,
        "active_value": "--enable-dwmac-intel",
        "inactive_value": None,
        "doc": "Build the dwmac-intel driver.",
        "default": None
    }, 
    "dwmac-intel-kernel-version": {
        "active": False,
        "active_value": "--with-dwmac-intel-kernel",
        "inactive_value": None,
        "doc": "dwmac-intel kernel version (optional).",
        "default": None
    },
    "e100": {
        "active": False,
        "active_value": "--enable-e100",
        "inactive_value": None,
        "doc": "Build the e100 driver.",
        "default": None
    },
    "e100-kernel-version": {
        "active": False,
        "active_value": "--with-e100-kernel",
        "inactive_value": None,
        "doc": "e100 kernel version (optional).",
        "default": None
    },
    "e1000": {
        "active": False,
        "active_value": "--enable-e1000",
        "inactive_value": None,
        "doc": "Enable the e1000 driver.",
        "default": None
    },
    "e1000-kernel-version": {
        "active": False,
        "active_value": "--with-e1000-kernel",
        "inactive_value": None,
        "doc": "e1000 kernel version (optional).",
        "default": None
    },
    "e1000e": {
        "active": False,
        "active_value": "--enable-e1000e",
        "inactive_value": None,
        "doc": "Enable the e1000e driver.",
        "default": None
    },
    "e1000e-kernel-version": {
        "active": False,
        "active_value": "--with-e1000e-kernel",
        "inactive_value": None,
        "doc": "e1000e kernel version (optional).",
        "default": None
    },
    "r8169": {
        "active": False,
        "active_value": "--enable-r8169",
        "inactive_value": None,
        "doc": "Enable the r8169 driver.",
        "default": None
    },
    "r8169-kernel-version": {
        "active": False,
        "active_value": "--with-r8169-kernel",
        "inactive_value": None,
        "doc": "r8169 kernel version (optional).",
        "default": None
    },
    "igb": {
        "active": False,
        "active_value": "--enable-igb",
        "inactive_value": None,
        "doc": "Enable the igb driver.",
        "default": None
    },
    "igb-kernel-version": {
        "active": False,
        "active_value": "--with-igb-kernel",
        "inactive_value": None,
        "doc": "igb kernel version (optional).",
        "default": None
    },
    "igc": {
        "active": False,
        "active_value": "--enable-igc",
        "inactive_value": None,
        "doc": "Build the igc driver.",
        "default": None
    }, 
    "igc-kernel-version": {
        "active": False,
        "active_value": "--with-igc-kernel",
        "inactive_value": None,
        "doc": "igc kernel version (optional).",
        "default": None
    },
    "stmmac-pci": {
        "active": False,
        "active_value": "--enable-stmmac-pci",
        "inactive_value": None,
        "doc": "Build the stmmac-pci driver.",
        "default": None
    }, 
    "stmmac-pci-kernel-version": {
        "active": False,
        "active_value": "--with-stmmac-pci-kernel",
        "inactive_value": None,
        "doc": "stmmac-pci kernel version (optional).",
        "default": None
    },
    "ccat": {
        "active": False,
        "active_value": "--enable-ccat",
        "inactive_value": None,
        "doc": "Enable the CCAT driver (independent of kernel version).",
        "default": None
    },
    "kernel": {
        "active": True,
        "active_value": "--enable-kernel",
        "inactive_value": None,
        "doc": "Build the master kernel modules.",
        "default": "--enable-kernel"
    },
    "rtdm": {
        "active": False,
        "active_value": "--enable-rtdm",
        "inactive_value": None,
        "doc": "Create the RTDM interface (RTAI or Xenomai directory needed).",
        "default": None
    },
    "debug-if": {
        "active": False,
        "active_value": "--enable-debug-if",
        "inactive_value": None,
        "doc": "Create a debug interface for each master.",
        "default": None
    },
    "debug-ring": {
        "active": False,
        "active_value": "--enable-debug-ring",
        "inactive_value": None,
        "doc": "Create a debug ring to record frames.",
        "default": None
    },
    "eoe": {
        "active": False,
        "active_value": "--enable-eoe",
        "inactive_value": None,
        "doc": "Enable Ethernet over EtherCAT (EoE) support.",
        "default": "--enable-eoe"
    },
    "cycles": {
        "active": False,
        "active_value": "--enable-cycles",
        "inactive_value": None,
        "doc": "Use CPU timestamp counter for finer timing calculation (Intel architecture).",
        "default": None
    },
    "hrtimer": {
        "active": False,
        "active_value": "--enable-hrtimer",
        "inactive_value": None,
        "doc": "Use high-resolution timer to let the master state machine sleep between sending frames.",
        "default": None
    },
    "regalias": {
        "active": False,
        "active_value": "--enable-regalias",
        "inactive_value": None,
        "doc": "Read alias address from register.",
        "default": None
    },
    "tool": {
        "active": True,
        "active_value": "--enable-tool",
        "inactive_value": None,
        "doc": "Build the command-line tool 'ethercat'.",
        "default": "--enable-tool"
    },
    "userlib": {
        "active": True,
        "active_value": "--enable-userlib",
        "inactive_value": None,
        "doc": "Build the userspace library.",
        "default": None
    },
    "tty": {
        "active": False,
        "active_value": "--enable-tty",
        "inactive_value": None,
        "doc": "Build the TTY driver.",
        "default": None
    },
    "wildcards": {
        "active": False,
        "active_value": "--enable-wildcards",
        "inactive_value": None,
        "doc": "Enable 0xffffffff to be used as wildcards for vendor ID and product code.",
        "default": None
    },
    "sii-assign": {
        "active": False,
        "active_value": "--enable-sii-assign",
        "inactive_value": None,
        "doc": "Enable assigning SII access to the PDI layer during slave configuration.",
        "default": None
    },
    "rt-syslog": {
        "active": True,
        "active_value": "--enable-rt-syslog",
        "inactive_value": None,
        "doc": "Enable syslog statements in real-time context.",
        "default": "--enable-rt-syslog"
    }
}

# The list of all possible supported modules for the EtherCAT master
doc_supported_modules = {
    "1.5" : "https://docs.etherlab.org/ethercat/1.5/doxygen/devicedrivers.html",
    "1.6" : "https://docs.etherlab.org/ethercat/1.6/doxygen/devicedrivers.html"
}

all_possible_supported_modules = ["8139too", "bcmgenet", "dwmac-intel", "e100", "e1000", "e1000e", "igb", "igc", "r8169", "stmmac-pci"]
variant_A_supported_modules = ["8139too", "e100", "e1000", "e1000e", "r8169"]
supported_modules = {
    "1.6" : 
    { 
        "igh_version" : "1.6",
        "kernels" : { 
            "6.12": all_possible_supported_modules,
            "6.6" : ["igc"] ,
            "6.4" : all_possible_supported_modules ,
            "6.1" : all_possible_supported_modules ,
            "5.15" : variant_A_supported_modules + ["igb", "igc"]  ,
            "5.14" : variant_A_supported_modules + ["bcmgenet","igb", "igc"]  ,
            "5.10" : variant_A_supported_modules + ["bcmgenet","igb"]  ,
            "5.4" : ["e100", "e1000e"] ,
            "4.19" : ["igb"] ,
            "4.4" :  variant_A_supported_modules + ["igb"] ,
            "3.18" : ["igb"] ,
            "3.16" :  variant_A_supported_modules ,
            "3.14" :  variant_A_supported_modules ,
            "3.12" :  variant_A_supported_modules ,
            "3.10" :  variant_A_supported_modules ,
            "3.8" :  variant_A_supported_modules ,
            "3.6" :  variant_A_supported_modules ,
            "3.4" :  variant_A_supported_modules ,
            "3.2" :  ["8139too", "e1000e", "r9169"] ,
            "3.0" :  ["8139too", "e100", "e1000"]  
        }
    },
    "1.5" : { 
        "igh_version" : "1.5",
        "kernels" : {
            "6.6" : ["igc"] ,
            "6.4" : ["e100", "igc"] ,
            "6.1" : all_possible_supported_modules ,
            "5.15": variant_A_supported_modules + ["igb", "igc"] ,
            "5.14": variant_A_supported_modules + ["bcmgenet", "igb", "igc"] ,
            "5.10": variant_A_supported_modules + ["bcmgenet", "igb"] ,
            "5.4": ["e100", "e1000e"] ,
            "4.19": ["igb"] ,
            "4.4": variant_A_supported_modules + ["igb"] ,
            "3.18": ["igb"] ,
            "3.16": variant_A_supported_modules ,
            "3.14": variant_A_supported_modules ,
            "3.12": variant_A_supported_modules ,
            "3.10": variant_A_supported_modules ,
            "3.8": variant_A_supported_modules ,
            "3.6": variant_A_supported_modules ,
            "3.4": variant_A_supported_modules ,
            "3.2": ["8139too", "e1000e", "r9169"] ,
            "3.0": ["8139too", "e100", "e1000"] 
        }
    }
}