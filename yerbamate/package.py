# A Mate package, with type, name, source, version, and dependencies
# This is the base class for all packages.
# A package could be a Model, Trainer, DataModule and so on.
# A package needs to have a install method, which will be called by the package manager?
# License: GPL v3

import os
import sys
import shutil
import urllib


class Package:

    # Type could become Enum, for now it's a string e.g. "model", "trainer"
    # Source could be a URL, or a local path?
    # Destination could be a local path, for example "models", "trainers", "data", "models/vit", "models/cnn/resnet"
    def __init__(self, type: str, destination: str):
        self.type = type
        self.source = source  # find a way to read the source
        self.destination = destination

    @staticmethod
    def install(source: str, destination: str):
        pass

    def _generate_signature(self, filename: str) -> dict:
        pass

    def _parse_signature(self, args: dict) -> object:
        pass

    def update(self) -> None:
        pass

    def uninstall(self) -> None:
        pass

    def __str__(self):
        return f"Package: {self.type} {self.source}"
