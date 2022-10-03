from ..package import Package
import os
import ipdb
from .package_metadata import ModelMetadataGenerator


class MetadataGenerator:
    def __init__(self, root_module: str, root_package: Package = None) -> None:
        # TODO root_package should have at least the author, type, version, description

        self.root_module = root_module
        self.root_package = root_package
        self.sub_modules = self.list_submodules()
        self.model_modules = self.list_model_modules()
        self.trainer_modules = self.list_trainer_modules()
        self.data_modules = self.list_data_modules()

        self.generate_model_metadata()

    # should generate a metadata package for the whole project
    def generate(self) -> dict:
        pass

    def generate_model_metadata(self) -> dict:
        return {
            model_module: ModelMetadataGenerator(
                self.root_module, "models", model_module
            ).generate()
            for model_module in self.model_modules
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

    def list_model_modules(self) -> list:
        return self.list_module([self.root_module, "models"])

    def list_trainer_modules(self) -> list:
        return self.list_module([self.root_module, "trainers"])

    def list_data_modules(self) -> list:

        return self.list_module([self.root_module, "data_loaders"])
