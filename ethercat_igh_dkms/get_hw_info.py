import subprocess

from logging import Logger
from typeguard import typechecked
from typing import Optional
from enum import Enum, unique
import re


@unique
class EthernetHardwares(Enum):
    """
    Enum class for the different types of Ethernet hardware
    """
    UNKNOWN = 0
    PCI = 1
    PCI_EXPRESS = 2
    USB = 3
    ONBOARD = 4
    LEGACY = 5


ethernet_device_types = {
    EthernetHardwares.PCI: {
        "pattern": r'enp[0-9]+s[0-9]+',
        "description": "PCI ethernet interfaces called enpXsY, based on PCI bus location",
        "short description": "PCI ethernet interface"
    },
    EthernetHardwares.PCI_EXPRESS: {
        "pattern": r'ens[0-9]+',
        "description": "PCI express ethernet interfaces called ensX, based on PCI express slots",
        "short description": "PCI express ethernet interface"
    },
    EthernetHardwares.USB: {
        "pattern": r'enx[0-9a-fA-F:]+',
        "description": "USB ethernet interfaces called enx<MAC>, based on the MAC address",
        "short description": "USB ethernet interface"
    },
    EthernetHardwares.ONBOARD: {
        "pattern": r'eno[0-9]+',
        "description": "on board ethernet interfaces called enoX, based on the order detected by the kernel",
        "short description": "On board ethernet interface"
    },
    EthernetHardwares.LEGACY: {
        "pattern": r'eth[0-9]+',
        "description": "legacy ethernet interfaces called ethX, based on the order detected by the kernel",
        "short description": "Legacy ethernet interface"
    }
}


@typechecked
def get_hw_info(interface: str, logger: Logger) -> Optional[str]:
    # readlink the data associated with the interface
    cmd = f"readlink /sys/class/net/{interface}/device"
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, stdout=subprocess.PIPE)
        return result.stdout.decode().strip()
    except Exception as e:
        logger.info(
            f"Could not get hardware information for interface {interface}. Exception: {e}")
        return None


@typechecked
def get_hw_type(interface: str, logger: Logger) -> EthernetHardwares:
    for hw_type, hw_info in ethernet_device_types.items():
        if re.match(hw_info["pattern"], interface):
            return hw_type
    return EthernetHardwares.UNKNOWN


@typechecked
def get_more_hw_info(hw_addr: str, type: EthernetHardwares, logger: Logger) -> Optional[str]:

    try:
        if type == EthernetHardwares.UNKNOWN:
            return None
        # Get the interesting part of the hardware address
        hw1 = hw_addr.split('/')[-1]
        type_info = ethernet_device_types[type]
        if type == EthernetHardwares.USB:
            usb_split = hw1.split('-')
            bus = usb_split[0]
            data_usb_split = usb_split[1].split(':')
            port = data_usb_split[0]
            interface_number = data_usb_split[1]
            info = type_info["short description"]
            return f"{info} bus: {bus}, port: {port}, interface number: {interface_number}"
        else:
            colon_split = hw1.split(':')
            info = type_info["short description"]
            if 3 == len(colon_split):
                # Get only the par of the hardware address after the first colon
                hw2 = colon_split[1] + ':' + colon_split[2]
                cmd = f"lspci -v -s {hw2}"
                result = subprocess.run(
                    cmd, shell=True, check=True, stdout=subprocess.PIPE)
                return info + "\n" + result.stdout.decode().strip()
            else:
                return info
    except Exception as e:
        logger.info(
            f"Could not get more information for hardware address {hw_addr}. Exception: {e}")
        return None


@typechecked
def get_all_hw_infos(interfaces: list[str], logger: Logger) -> dict:
    infos = {}
    for interface in interfaces:
        infos[interface] = get_hw_info(interface, logger)
    return infos
