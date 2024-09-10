#! /usr/bin/python3
"""
To run the different tests:
poetry install --with test
poetry run pytest -s tests/test_build.py::TestBuild::test_build
poetry run pytest -s tests/test_build.py::TestBuild::test_update
poetry run pytest -s tests/test_build.py::TestBuild::test_produce_dkms_cfg_file
"""
import unittest
import os
import subprocess
import shutil

import ethercat_igh_dkms as edkms

current_dir = os.path.dirname(os.path.abspath(__file__))


class TestBuild(unittest.TestCase):
    def build_and_test(self):
        if None == edkms.get_logger():
            edkms.create_logger("ethercat_igh_dkms", "tests/log/")
            """
            when using from module_a import *.
            When you do this, a copy of the my_glob variable is imported into the current module,
            rather than a reference to the original global variable in module_a.
            """
        edkms.get_logger().info("Test build")
        # Set the source and destination directories locally
        edkms.set_configure_prefix(
            os.path.join(current_dir, "local", "etherlab"))
        build_dir = os.path.join(current_dir, "src")
        edkms.set_src_install(build_dir)
        edkms.set_src_dest("ethercat")
        # Actually call the build function
        edkms.build_module()
        # Check that the kernel modules ec_master.ko, ec_xxxx.ko have been built in the build dir
        # Find the kernel modules inside build dir
        cmd = "find "+build_dir+" -name '*.ko'"
        result = subprocess.run(
            cmd, shell=True, check=True, stdout=subprocess.PIPE)
        kernel_modules = result.stdout.decode().split("\n")
        # remove empty strings
        kernel_modules = [k for k in kernel_modules if "" != k]
        # Display built modules
        pretty_print = ""
        for k in kernel_modules:
            pretty_print = pretty_print + "tests/" + \
                k.split("tests/")[1] + " ; "
        pretty_print = pretty_print[:-3]
        edkms.get_logger().info(f"Built modules: {pretty_print}")
        # Check that ec_master.ko is in the list
        # Check that in devices ec_xxxx.ko is in the list  of known device modules
        for k in kernel_modules:
            sp = k.split("/")
            dir = sp[-2]
            mod = sp[-1].split(".")[0]
            if "master" == dir:
                self.assertEqual(mod, "ec_master")
            elif "devices" == dir:
                mod = mod[3:]  # remove the ec_ prefix
                self.assertTrue(mod in edkms.known_device_modules)
        self.build_dir = build_dir

    def test_build(self):
        self.build_and_test()
        # Remove the build directory
        shutil.rmtree(self.build_dir)

    def test_update(self):
        if None == edkms.get_logger():
            edkms.create_logger("ethercat_igh_dkms", "tests/log/")
            """
            when using from module_a import *.
            When you do this, a copy of the my_glob variable is imported into the current module,
            rather than a reference to the original global variable in module_a.
            """
        edkms.get_logger().info("Test update an existing build directory")
        # Set the source and destination directories locally
        edkms.set_configure_prefix(
            os.path.join(current_dir, "local", "etherlab"))
        src_install = os.path.join(current_dir, "src")
        edkms.set_src_install(src_install)
        edkms.set_src_dest("ethercat")
        edkms.get_logger().info("Donwload the source code a first time...")
        edkms.clone()
        edkms.get_logger().info(
            "Build the source code with an already source code directory existing...")
        # Actually call the build function
        self.test_build()

    def test_produce_dkms_cfg_file(self):
        if None == edkms.get_logger():
            edkms.create_logger("ethercat_igh_dkms", "tests/log/")
        edkms.get_logger().info("Test produce dkms configuration file")
        # Set the source and destination directories locally
        edkms.set_configure_prefix(
            os.path.join(current_dir, "local", "etherlab"))
        src_install = os.path.join(current_dir, "src")
        edkms.set_src_install(src_install)
        self.build_and_test()
        # Produce the dkms configuration file
        edkms.create_dkms_config()
        # Check that the dkms configuration file has been produced correctly
        dkms_cfg_file = os.path.join(edkms.def_source_dir(), "dkms.conf")
        self.assertTrue(os.path.exists(dkms_cfg_file))
        # Read the dkms configuration file
        with open(dkms_cfg_file, "r") as f:
            dkms_content = f.read()
        # Open example file and check that the content is the same
        project_dir = os.path.dirname(current_dir)
        example_file = os.path.join(project_dir, "dkms", "dkms.conf.example")
        with open(example_file, "r") as f:
            example_content = f.read()
        if dkms_content != example_content:
            edkms.get_logger().error(
                "dkms configuration file does not match the example file: produced file:\n{dkms_content}\n expected file:\n{example_content}")
        self.assertEqual(dkms_content, example_content)
        # Remove the build directory
        shutil.rmtree(self.build_dir)


if __name__ == '__main__':
    unittest.main()
