import json
import sys
from yerbamate.mate_config import MateConfig
from yerbamate.utils.bunch import Bunch

# from ..source import DataSource
from glob import glob
import os
from typing import Optional
import ipdb
from ..project_parser.project_parser import ProjectParser
from . import io
from typing import Any


class LocalDataSource:
    def __init__(
        self,
        config: MateConfig,
        # root_dir: str = ".",  # a different root (".mate") is used while installing a packaage installing a package, we can use the root dir of the package
    ):
        super().__init__()

        root_dir = config.project
        self.root_folder = root_dir
        self.config = config

        ProjectParser.check_project_structure(root_dir)

        self.__load_data(root_dir)

    def get_all_experiments(self) -> dict[str, Any]:
        exps = self.list("experiments")

        results = {}
        for experiment in exps:
            exp, _ = self.load_experiment(experiment)
            results[experiment] = exp

        return results

    def assert_experiment_exists(self, experiment):
        assert experiment in self.experiments, f"Experiment {experiment} does not exist"

    def load_metadata(self, experiment):

        exp = io.read_json(
            os.path.join(self.root_folder, "experiments", experiment, f"metadata.json")
        )

        return exp

    def load_experiment(self, experiment: str):

        exp = io.read_experiments(self.config, self.root_folder, experiment)
        self.save_path = os.path.join(self.config.results_folder, experiment)
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        return exp, self.save_path

    def load_mate_config_and_root(self):
        return self.__findroot()

    def save_toml(self, toml, experiment_name):
        io.save_toml(self.root_folder, experiment_name, toml)

    def save_metadata(self, experiment, metadata):

        io.save_metadata(self.root_folder, experiment, metadata)

    def save_experiment(self, experiment):
        save_path = io.get_experiment_path(self.root_folder, experiment)
        with open(save_path, "w") as f:
            f.write(json.dumps(experiment, indent=4))

    def __load_data(self, root_dir: str):
        self.models = self.__filter_regular_folders(
            os.listdir(os.path.join(root_dir, "models"))
        )
        self.trainers = self.__filter_regular_folders(
            os.listdir(os.path.join(root_dir, "trainers"))
        )
        self.data_loaders = self.__filter_regular_folders(
            os.listdir(os.path.join(root_dir, "data"))
        )

        self.experiments = [
            os.path.basename(dir)
            for dir in glob(os.path.join(root_dir, "experiments", "*"))
            if dir and not "__" in dir
        ]

        self.map = {
            "models": self.models,
            "trainers": self.trainers,
            "data_loaders": self.data_loaders,
            "experiments": self.experiments,
        }
        self.map = {k: v for k, v in self.map.items()}

    def __filter_regular_folders(self, names: list[str]):
        return [fn for fn in names if not fn.startswith("__")]

    def __filter_names(self, query: Optional[str], names: list[str]):
        return names if query is None else [name for name in names if query == name]

    def list(self, module: str, query: Optional[str] = None):

        # if module is None, return all modules
        if module is None:
            return self.map
        assert module in self.map.keys(), f"Folder {module} not found"
        return self.__filter_names(query, self.map[module])

    def __findroot(self):
        """
        Method in charge of finding the root folder of the project and reading the content of mate.json
        """
        self.root_folder, self.config = io.find_root()
        self.root_save_folder = self.config.results_folder
        self.save_path = self.root_save_folder
        return self.config, self.root_folder, self.root_save_folder

    def __validate_missing_params(
        self,
        root: Bunch,
        model_name: str,
        experiment: str,
        generate_defaults: bool = False,
    ):
        """
        Validates that all the required parameters are present in the params file
        """

        parsed_params, errors = self.trainer.generate_full_dict()

        if len(errors) > 0:
            print(f"Errors in {model_name}/{experiment}")
            for error in errors:
                print(error)

            # io.update_hyperparameters(
            #     self.root_folder, model_name, experiment, parsed_params
            # )
            sys.exit(1)

        return parsed_params

    def __parse_and_validate_params(self, trainer, experiment: str):
        assert (
            self.trainer is not None
        ), "Trainer must be initialized before parsing params (Bombilla is managed by Trainer)"

        full, err = trainer.generate_full_dict()

        if len(err) > 0:
            print(f"Errors in {experiment}")
            for error in err:
                print(error)

            # io.update_hyperparameters(self.root_folder, model_name, params, full)
            sys.exit(1)

        io.save_train_experiments(self.save_path, full, self.config)

        return full

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
