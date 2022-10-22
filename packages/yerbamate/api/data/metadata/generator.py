from typing import Any

from yerbamate.api.data.sources.local import LocalDataSource

from .metadata import BaseMetadata, Metadata
from ..package import Package
import os
import ipdb
from .package_metadata import ModuleMetadataGenerator


class MetadataGenerator:
    def __init__(
        self, root_module: str, metadata: BaseMetadata, local_ds: LocalDataSource
    ) -> None:
        # TODO root_package should have at least the author, type, version, description

        self.root_module = root_module
        self.root_meta = metadata
        self.local_ds = local_ds
        self.sub_modules = self.list_submodules()
        self.two_level_modules = ("data",)
        self.cached_metadata = None

    # should generate a metadata package for the whole project
    def generate(self) -> dict:

        if self.cached_metadata:
            return self.cached_metadata

        modules = self.list_module([self.root_module])
        gen = {module: self.generate_module_metadata(module) for module in modules}
        self.cached_metadata = gen
        return self.cached_metadata

    def generate_module_metadata(self, module: str) -> dict:
        result = {}
        for sub_module in self.list_module([self.root_module, module]):

            if module in self.two_level_modules:
                result[sub_module] = {}
                for thub_module in self.list_module(
                    [self.root_module, module, sub_module]
                ):
                    result[sub_module][thub_module] = ModuleMetadataGenerator(
                        [self.root_module, module, sub_module, thub_module],
                        self.root_meta,
                        self.local_ds,
                    ).generate()
            else:
                result[sub_module] = ModuleMetadataGenerator(
                    [self.root_module, module, sub_module],
                    self.root_meta,
                    self.local_ds,
                ).generate()
        return result



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
