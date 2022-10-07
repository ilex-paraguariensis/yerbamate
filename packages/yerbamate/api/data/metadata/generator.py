from typing import Any

from yerbamate.api.data.sources.local import LocalDataSource

from .metadata import BaseMetadata, Metadata
from ..package import Package
import os
import ipdb
from .package_metadata import ModuleMetadataGenerator


class MetadataGenerator:
    def __init__(
        self, root_module: str, metadata: Metadata, local_ds: LocalDataSource
    ) -> None:
        # TODO root_package should have at least the author, type, version, description

        self.root_module = root_module
        self.root_meta = metadata
        self.local_ds = local_ds
        self.sub_modules = self.list_submodules()

    # should generate a metadata package for the whole project
    def generate(self) -> dict:
        model_meta = self.generate_module_metadata("models")
        trainer_meta = self.generate_module_metadata("trainers")
        data_meta = self.generate_module_metadata("data_loaders")
        return {
            "models": model_meta,
            "trainers": trainer_meta,
            "data_loaders": data_meta,
        }

    def generate_module_metadata(self, module: str) -> dict:
        return {
            model_module: ModuleMetadataGenerator(
                self.root_module, module, model_module, self.root_meta, self.local_ds
            ).generate().to_dict()
            for model_module in self.list_modules(module)
        }

    # returns a list of submodules in the root module, should be models, trainers, data
    def list_submodules(self) -> list:
        return self.list_module([self.root_module])

    def list_module(self, modules: list) -> list:
        base_path = os.path.join(*modules)
        return [
            dir
            for dir in os.listdir(base_path)
            if os.path.isdir(os.path.join(base_path, dir))
            and os.path.exists(os.path.join(base_path, dir, "__init__.py"))
        ]

    def list_modules(self, module: str) -> list:
        return self.list_module([self.root_module, module])
