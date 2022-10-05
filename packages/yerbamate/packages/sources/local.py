from .source import DataSource
import os
from typing import Optional
import ipdb
from ..project_parser.project_parser import ProjectParser


class LocalDataSource(DataSource):
    def __init__(
        self,
        root_dir: str = ".",  # a different root (".mate") is used while installing a packaage installing a package, we can use the root dir of the package
    ):
        super().__init__()
        ProjectParser.check_project_structure(root_dir)
        self.models = self.__filter_regular_folders(
            os.listdir(os.path.join(root_dir, "models"))
        )
        self.trainers = self.__filter_regular_folders(
            os.listdir(os.path.join(root_dir, "trainers"))
        )
        self.data_loaders = self.__filter_regular_folders(
            os.listdir(os.path.join(root_dir, "data_loaders"))
        )
        self.experiments = [
            os.path.splitext(exp_name)[0]
            for exp_name in os.listdir(os.path.join(root_dir, "experiments"))
            if ".json" in exp_name
        ]

        self.map = {
            "models": self.models,
            "trainers": self.trainers,
            "data_loaders": self.data_loaders,
            "experiments": self.experiments,
        }

        self.packages = []  # TODO: what's this?

    def __filter_regular_folders(self, names: list[str]):
        return [fn for fn in names if not fn in ["__pycache__", "__init__.py"]]

    def __filter_names(self, query: Optional[str], names: list[str]):
        return names if query is None else [name for name in names if query == name]

    def list(self, module: str, query: Optional[str] = None):
        assert module in self.map.keys(), f"Folder {module} not found"
        return self.__filter_names(query, self.map[module])

    def get_models(self, query: Optional[str] = None):
        return self.__filter_names(query, self.models)

    def get_trainers(self, query: Optional[str] = None):
        return self.__filter_names(query, self.trainers)

    def get_data_loaders(self, query: Optional[str] = None):
        return self.__filter_names(query, self.data_loaders)

    def get_experiments(self, query: Optional[str] = None):
        return self.__filter_names(query, self.experiments)

    def get_packages(self, query: Optional[str] = None):
        return self.packages

    def add_model(self, model):
        self.models.append(model)

    def add_trainer(self, trainer):
        self.trainers.append(trainer)

    def add_data_loader(self, dataset):
        self.data_loaders.append(dataset)

    def add_experiment(self, experiment):
        self.experiments.append(experiment)

    def add_package(self, package):
        self.packages.append(package)
