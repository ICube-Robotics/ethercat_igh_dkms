#! /usr/bin/python3
"""
To run that test:
poetry install --with test
poetry run pytest -s tests/test_write_config_file.py::TestWriteConfigFile::test_write_config_file
"""

import unittest
import shutil
from datetime import datetime
from dateutil import tz
import os
from pathlib import Path

import ethercat_igh_dkms as edkms

date_format = "%Y_%m_%d__%Hh%Mmin%Ss_%Z"

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = Path(current_dir).parent


class TestWriteConfigFile(unittest.TestCase):
    def setUp(self):
        os.chdir(current_dir)
        if None == edkms.get_logger():
            edkms.create_logger("ethercat_igh_dkms",
                                os.path.join(current_dir, "log"))
            """
            when using from module_a import *.
            When you do this, a copy of the my_glob variable is imported into the current module,
            rather than a reference to the original global variable in module_a.
            """

    def test_write_config_file(self):
        edkms.get_logger().info("Test write configuration file")
        # Get a string representing the date and time
        id_date_time = datetime.now(tz=tz.tzutc()).strftime(date_format)
        cfg_name = project_dir.joinpath("tests/ethercat.config_file.template")
        working_cfg_name = project_dir.joinpath(
            "tests/ethercat.config_file."+id_date_time)
        # Copy the template configuration file to the current directory
        shutil.copy(cfg_name, working_cfg_name)
        edkms.set_interactive(False)
        edkms.update_ethercat_config(str(working_cfg_name))
        # Read the working configuration file
        with open(working_cfg_name, "r") as f:
            lines = f.readlines()
            # Check that MASTER0_DEVICE is set (line begining with MASTER0_DEVICE) and stores a proper MAC address
            MASTER0_DEVICE_found = False
            for line in lines:
                if line.startswith("MASTER0_DEVICE"):
                    MASTER0_DEVICE_found = True
                    # Check that the MAC address is valid
                    addr = line.split("=")[1].strip().replace('"', "")
                    self.assertTrue(edkms.check_hex_mac_address(addr))
            self.assertTrue(MASTER0_DEVICE_found)
            # Check that the DEVICE_MODULES is set (line begining with DEVICE_MODULES) and stores a proper value
            DEVICE_MODULES_found = False
            for line in lines:
                if line.startswith("DEVICE_MODULES"):
                    DEVICE_MODULES_found = True
                    # Check that the value is in the list of known device modules
                    value = line.split("=")[1].strip().replace('"', "")
                    self.assertTrue(value in edkms.known_device_modules)
            self.assertTrue(DEVICE_MODULES_found)
        # remove the working file
        os.remove(working_cfg_name)


if __name__ == '__main__':
    unittest.main()
