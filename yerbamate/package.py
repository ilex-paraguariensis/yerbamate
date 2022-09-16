# A Mate package, with type, name, source, version, and dependencies
# This is the base class for all packages.
# A package could be a Model, Trainer, DataModule and so on.
# A package needs to have a install method, which will be called by the package manager?
# License: GPL v3

import os
import sys
import shutil
import torch as t
import urllib


class Package:

    # Type could become Enum, for now it's a string e.g. "model", "trainer"
    # Source could be a URL, or a local path?
    # Destination could be a local path, for example "models", "trainers", "data", "models/vit", "models/cnn/resnet"
    def __init__(self, type: str, source: str, destination: str):
        self.type = type
        self.source = source
        self.destination = destination

    # do we need to use @abstractmethod? I don't think its necessary in python
    # we could have a default install method, which just clones the repo in ".mate_cache", and then copies it to the destination
    def install(self):
        pass

    # we can add more methods here, like uninstall, update, etc.

    def __str__(self):
        return f"Package: {self.type} {self.source}"
