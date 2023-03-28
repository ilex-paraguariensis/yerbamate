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
from ...utils.bunch import Bunch

import inspect
import ipdb


class Package:

    # Type could become Enum, for now it's a string e.g. "model", "trainer"
    # Source could be a URL, or a local path?
    # Destination could be a local path, for example "models", "trainers", "data", "models/vit", "models/cnn/resnet"
    def __init__(
        self,
        params: Bunch = None,
        root: str = None,
        backbone: str = None,
        source: str = None,
        package: str = None,
        type: str = None,
        url: str = None,
        export: Bunch = None,
        description: str = None,
        version: str = None,
        author: str = None,
        license: str = None,
        pip: Bunch = None,
    ):
        self.type = type
        self.source = source  # find a way to read the source
        self.root = root
        self.backbone = backbone
        self.url = url
        self.params = params

        self.export = export
        self.package = package

        self.description = description
        self.version = version
        self.author = author
        self.type = type
        # self.object = self._object()

    @staticmethod
    def install(source: str, destination: str):
        pass

    def _get_package_class(self, package_location: str, package_name: str) -> dict:
        # package_name = package_location.split(".")[-1]
        # package_class_name = package_name.title().replace("_", "")
        package = __import__(
            package_location,
            fromlist=[package_location.split(".")[1]],
        )
        package_class = getattr(package, package_name)
        ipdb.set_trace()
        return package_class

    def _generate_signature(self, entrypoint: Union[Type, Callable]) -> dict:
        return inspect.getfullargspec(entrypoint).args  # TODO: turn it into a dict

    def _parse_signature(self, args: dict) -> object:
        return self._get_package_class(self.root, self.source)(**args)

    def _object(self) -> object:
        # return self._parse_signature(self.params)
        return self._get_package_class(self.root, self.source)

    def update(self) -> None:
        pass

    def uninstall(self) -> None:
        pass

    def __str__(self):
        return f"Package: {self.type} {self.source}"


class PLTrainerPackage(Package):

    # TODO automatically parse root, package, version from mate config

    # only params are required
    def __init__(
        self,
        params: Bunch = None,
        root: str = None,
        backbone: str = "torch",
        source: str = "local",
        package: str = None,
        type: str = "pl_train",
        url: str = None,
        export: Bunch = None,
        description: str = None,
        version: str = None,
    ):
        super().__init__(
            root=root,
            backbone=backbone,
            source=source,
            package=package,
            type=type,
            url=url,
            params=params,
            export=export,
            description=description,
            version=version,
        )
