import json
import sys
from yerbamate.utils.bunch import Bunch
from ..source import DataSource
from glob import glob
import os
from typing import Optional
import ipdb
from ..local import io
from typing import Any


class LocalDataSource(DataSource):
    def __init__(
        self,
        config,
        # root_dir: str = ".",  # a different root (".mate") is used while installing a packaage installing a package, we can use the root dir of the package
    ):
        super().__init__()

        root_dir = config["project"]
        self.root_folder = root_dir
        self.config = config
        self.map = None

        # ProjectParser.check_project_structure(root_dir)

        self.__load_data(root_dir)

    def load_mate_config_and_root(self):
        return self.__findroot()

    def summary(self):
        self.__load_data(self.root_folder)
        return self.map

    def __load_data(self, root_dir: str):

        if self.map != None:
            return

        self.map = {}
        for dir in os.listdir(root_dir):

            if dir == "experiments":
                self.map["experiments"] = {
                    dir: [
                        exp_file
                        for exp_file in os.listdir(
                            os.path.join(root_dir, "experiments", dir)
                        )
                        if ".py" in exp_file and exp_file != "__init__.py"
                    ]
                    for dir in os.listdir(os.path.join(root_dir, "experiments"))
                    if os.path.isdir(os.path.join(root_dir, "experiments", dir))
                    and dir != "__pycache__"
                    or (".py" in dir and dir != "__init__.py")
                }
                # self.map["experiments"] =  exps.values
            else:
                if os.path.isdir(os.path.join(root_dir, dir)) and dir != "__pycache__":
                    # see if there is a __init__.py file
                    if "__init__.py" in os.listdir(os.path.join(root_dir, dir)):
                        self.map[dir] = [
                            sub_dir
                            for sub_dir in os.listdir(os.path.join(root_dir, dir))
                            if os.path.isdir(os.path.join(root_dir, dir, sub_dir))
                            and os.path.exists(
                                os.path.join(root_dir, dir, sub_dir, "__init__.py")
                            )
                            and sub_dir != "__pycache__"
                        ]
        # ipdb.set_trace()
        # self.map = {k: v for k, v in self.map.items()}

    def __filter_regular_folders(self, names: list[str]):
        return [fn for fn in names if not fn.startswith("__")]

    def __filter_names(self, query: Optional[str], names: list[str]):
        return names if query is None else [name for name in names if query == name]

    def list(self, module: str):

        if module is None:
            return self.map
        # ipdb.set_trace()
        assert module in self.map.keys(), f"Module {module} not found"
        return self.map[module]

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
