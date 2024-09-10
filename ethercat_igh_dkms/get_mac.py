import netifaces
import sys
from typeguard import typechecked
import logging
import re
from logging import Logger


@typechecked
def get_all_interfaces(logger: Logger) -> list:
    try:
        return netifaces.interfaces()
    except Exception as e:
        logger.warning(f"Could not get network interfaces. Exception: {e}")
        return []


@typechecked
def identify_ethernet_interfaces(logger: Logger) -> list:
    """
    Identify Ethernet interfaces that are likely come from 
    ethernet boards likely to be used for EtherCAT.
    The order chosen is based on the most common names and is:
      1. legacy ethernet interfaces called ethX
      2. on board ethernet interfaces called enoX
      3. PCI express ethernet interfaces called enpXsY
      4. PCI ethernet interfaces called ensX
      5. USB ethernet interfaces called enxXXXXXXXXXXXX

    parameters:
    -----------
    logger: Logger
        Logger object to log messages

    returns:
    --------
    list
        List of Ethernet interfaces ordered such that the first is 
        the most likely to be used for EtherCAT.
    """
    try:
        interfaces = get_all_interfaces(logger)
        eth_reg = r'eth[0-9]+'
        enp_reg = r'enp[0-9]+s[0-9]+'
        ens_reg = r'ens[0-9]+'
        eno_reg = r'eno[0-9]+'
        enx_reg = r'enx[0-9a-fA-F:]+'
        regs = [eth_reg, eno_reg, ens_reg, enp_reg, enx_reg]
        ethernet_interfaces = []
        for reg in regs:
            for i in interfaces:
                if re.match(reg, i):
                    ethernet_interfaces.append(i)
                    break
        return ethernet_interfaces
    except Exception as e:
        logger.warning(f"Could not get network interfaces. Exception: {e}")
        return []


@typechecked
def get_mac_address(logger: Logger, interface: str = 'eth0') -> str:
    try:
        mac = netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']
        return mac
    except (ValueError, KeyError, IndexError) as e:
        logger.warning(
            f"Could not get MAC address for interface: {interface}. Exception: {e}")
        return None
