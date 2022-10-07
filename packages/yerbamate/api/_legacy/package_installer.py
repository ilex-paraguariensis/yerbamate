# A Wrapper for managing a package i.e., installing versioning etc.
import os
import sys
import shutil
import urllib
from typing import Union, Callable, Optional, Type


import inspect
import ipdb
from .package import Package


class PackageManager:

    # or list of packages, then install pacakge "name"?
    def __init__(self, package: Package):
        self.package = package

    def install(self):

        self.clone_repo()
        self.fix_import_bug()
        self.copy_files()

        # install requirements?
        # pip install -r requirements.txt

        self.post_install()

    def clone_repo(self):

        assert self.source == "git"

        # Clone the repo
        # git clone
        temp_dir = ".mate_temp"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.mkdir(temp_dir)
        os.system(f"git clone {self.url} {temp_dir}")

    def fix_import_bug(self):
        # change to relative import
        #

        pass

    # copy to destination
    def copy_files(self):
        pass

    # maybe generate a signature file for the package, so that we can check if the package is installed and what models are available
    def post_install(self):

        # delete .mate_temp dir
        # os.system("rm -rf .mate_temp")
        pass


class TorchPipModelPackage(PackageManager):
    def __init__(
        self,
        package: Package,
    ):
        super().__init__(package=package)

    def install(self):

        self.clone_repo()
        self.fix_import_bug()
        self.copy_files()

        # install requirements?
        # pip install -r requirements.txt

        self.post_install()

    def clone_repo(self):

        assert self.source == "git"

        # Clone the repo
        # git clone
        temp_dir = ".mate_temp"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.mkdir(temp_dir)
        os.system(f"git clone {self.url} {temp_dir}")

    def fix_import_bug(self):
        # change to relative import
        #

        pass

    # copy to destination
    def copy_files(self):
        pass

    # maybe generate a signature file for the package, so that we can check if the package is installed and what models are available
    def post_install(self):

        # delete .mate_temp dir
        # os.system("rm -rf .mate_temp")
        pass
