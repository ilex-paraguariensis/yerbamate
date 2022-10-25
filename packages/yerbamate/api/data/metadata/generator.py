from typing import Any

from yerbamate.api.data.sources.local import LocalDataSource

from .metadata import BaseMetadata, Metadata
from ..package import Package
import os
import ipdb
from .module_metadata_generator import ModuleMetadataGenerator
from .experiment_metadata_generator import ExperimentMetadataGenerator


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
    def generate(self, rewrite: bool = False) -> dict:

        print("Generating metadata... might take a while")

        if self.cached_metadata and not rewrite:
            return self.cached_metadata

        modules = self.list_module([self.root_module])
        gen = {
            module: self.generate_module_metadata(module, rewrite) for module in modules
        }

        exps = self.local_ds.list("experiments")
        gen["experiments"] = {
            exp: self.generate_experiment_metadata(exp) for exp in exps
        }

        self.cached_metadata = gen
        return self.cached_metadata

    def generate_experiment_metadata(self, experiment: str) -> dict:
        return ExperimentMetadataGenerator(
            experiment, self.root_module, self.root_meta, self.local_ds
        ).generate()

    def generate_module_metadata(self, module: str, rewrite: bool = False) -> dict:
        result = {}
        for sub_module in self.list_module([self.root_module, module]):

            if module in self.two_level_modules:
                result[sub_module] = {}
                for thub_module in self.list_module(
                    [self.root_module, module, sub_module]
                ):
                    # ipdb.set_trace()
                    result[sub_module][thub_module] = ModuleMetadataGenerator(
                        [self.root_module, module, sub_module, thub_module],
                        self.root_meta,
                        self.local_ds,
                    ).generate(rewrite)
            else:
                result[sub_module] = ModuleMetadataGenerator(
                    [self.root_module, module, sub_module],
                    self.root_meta,
                    self.local_ds,
                ).generate(rewrite)
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
