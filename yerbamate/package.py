# A Mate package, with type, name, source, version, and dependencies
# This is the base class for all packages.
# A package could be a Model, Trainer, DataModule and so on.
# A package needs to have a install method, which will be called by the package manager?
# License: GPL v3

import os
import sys
import shutil
import urllib
from typing import Union, Callable, Optional, Type

"""
{
    "root": "vit",
    "backbone": "torch",
    "source": "pip-package-source",
    "type": "model",
    "url": "https://github.com/lucidrains/vit-pytorch",
    "params": {
        "pip_package": "vit-pytorch",
        "pip_version": "0.22.0",
        "pip_requirements": "requirements.txt"
    },
    "export": {
        "type": "models",
        "root_dir": "vit",
        "models": [
            "ViT",
            "Dino",
            "CrossViT",
            "DeepViT",
            "CaiT",
            "T2TViT"
        ],
        "full_param_export_fle": "vit_full_params.json"
    },
    "description": "Vision Transformer (ViT) in PyTorch",
    "version": "0.22.0",
    "author": "lucidrains",
    "license": "MIT"
}
"""
from bunch import Bunch
import inspect


class Package:

    # Type could become Enum, for now it's a string e.g. "model", "trainer"
    # Source could be a URL, or a local path?
    # Destination could be a local path, for example "models", "trainers", "data", "models/vit", "models/cnn/resnet"
    def __init__(
        self,
        root: str,
        backbone: str,
        source: str,
        url: str,
        params: Bunch,
        export: Bunch,
        description: str,
        version: str,
        author: str,
        type: str,
    ):
        self.type = type
        self.source = source  # find a way to read the source
        self.root = root
        self.backbone = backbone
        self.url = url
        self.params = params
        # self.export
        self.description = description
        self.version = version
        self.author = author
        self.type = type

    @staticmethod
    def install(source: str, destination: str):
        pass

    def _get_package_class(self, package_location: str) -> dict:
        package_name = package_location.split(".")[-1]
        package_class_name = package_name.title().replace("_", "")
        to_load = f"{package_location}.{package_name}"
        package = __import__(
            to_load,
            fromlist=[package_location.split(".")[1]],
        )
        package_class = getattr(package, package_class_name)
        return package_class

    def _generate_signature(self, entrypoint: Union[Type, Callable]) -> dict:
        return inspect.getfullargspec(
            entrypoint
        ).args  # TODO: turn it into a dict

    def _parse_signature(self, args: dict) -> object:
        return self._get_package_class(self.source)(**args)

    def _object(self) -> object:
        return self._parse_signature(self.params)

    def update(self) -> None:
        pass

    def uninstall(self) -> None:
        pass

    def __str__(self):
        return f"Package: {self.type} {self.source}"


class TorchPipModelPackage(Package):
    def __init__(
        self,
        root: str,
        backbone: str,
        source: str,
        url: str,
        params: Bunch,
        export: Bunch,
        description: str,
        version: str,
    ):
        super().__init__(
            root, backbone, source, url, params, export, description, version
        )

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
