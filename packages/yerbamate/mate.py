import os

from .utils.bunch import Bunch

import json
import sys

from .trainers.trainer import Trainer
import ipdb
from .utils import utils
from . import io
from bombilla import parser

from typing import Optional
from .project_parser.project_parser import ProjectParser
from .mate_config import MateConfig


class Mate:
    @staticmethod
    def init(project_name: str):
        # should actually be a package install
        pass

    def __init__(self, init=False):
        self.root_folder = ""
        self.save_path = ""
        self.current_folder = os.path.dirname(__file__)
        self.config: Optional[MateConfig] = None
        self.__findroot()
        self.__update_mate_version()
        self.models = self.__list_packages("models")
        self.is_restart = False
        self.run_params = None
        self.custom_save_path = None
        self.trainer: Optional[Trainer] = None
        ProjectParser.check_project_structure(self.root_folder)

    def __list_packages(self, folder: str):
        return io.list_packages(self.root_folder, folder)

    def experiments(self, model_name: Optional[str] = None):
        io.list_experiments(self.root_folder, model_name, True)

    def __update_mate_version(self):
        utils.migrate_mate_version(self.config, self.root_folder)

    def __findroot(self):
        """
        Method in charge of finding the root folder of the project and reading the content of mate.json
        """
        self.root_folder, self.config = io.find_root()
        self.root_save_folder = self.config.results_folder
        self.save_path = self.root_save_folder

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

            io.update_hyperparameters(
                self.root_folder, model_name, experiment, parsed_params
            )
            sys.exit(1)

        return parsed_params

    def __load_exec_function(self, exec_file: str):
        return __import__(
            f"{self.root_folder}.exec.{exec_file}",
            fromlist=["exec"],
        ).run

    def __set_save_path(self, model_name: str, params_name: str):
        self.save_path = io.set_save_path(
            self.root_save_folder, self.root_folder, model_name, params_name
        )

    def __read_hyperparameters(self, model_name: str, hparams_name: str = "default"):

        hp = io.read_experiments(
            self.config,
            self.root_folder,
            model_name,
            hparams_name,
            self.run_params,
        )

        # # this function will exit the program if there are missing parameters
        # self.__validate_missing_params(hp, model_name, hparams_name)

        # # all params are now validated, we can update the whole generated file
        # all_params = self.__validate_missing_params(
        #     hp, model_name, hparams_name, generate_defaults=True
        # )

        # io.save_train_experiments(self.save_path, all_params, self.config)

        return hp

    def __parse_and_validate_params(self, model_name: str, params: str):
        assert (
            self.trainer is not None
        ), "Trainer must be initialized before parsing params (Bombilla is managed by Trainer)"

        full, err = self.trainer.generate_full_dict()

        if len(err) > 0:
            print(f"Errors in {model_name}/{params}")
            for error in err:
                print(error)

            # io.update_hyperparameters(self.root_folder, model_name, params, full)
            sys.exit(1)

        io.save_train_experiments(self.save_path, full, self.config)

        return full

    def __load_experiment_conf(self, model_name: str, params_name: str):
        params = self.__read_hyperparameters(model_name, params_name)
        self.__set_save_path(model_name, params_name)
        params.save_path = self.save_path
        params.root_folder = self.root_folder
        return params

    def __get_trainer(self, model_name: str, params: str):
        if self.trainer is None:

            conf = self.__load_experiment_conf(model_name, params)

            print(conf)

            map_key_value = {
                "save_path": self.save_path,
                "save_dir": self.save_path,
            }
            root_module = f"{self.root_folder}"
            base_module = io.get_experiment_base_module(
                self.root_folder, model_name, params
            )
            self.trainer = Trainer.create(conf, root_module, base_module, map_key_value)

        return self.trainer

    def create(self, path: str):
        pass

    def remove(self, model_name: str):
        io.remove(self.root_folder, model_name)

    def list(self, folder: str):

        if folder == "experiments":
            io.list_experiments(self.root_folder)
            return

        io.list(self.root_folder, folder)

    def clone(self, source_model: str, target_model: str):
        io.clone(self.root_folder, source_model, target_model)

    def snapshot(self, model_name: str):
        io.snapshot(self.root_folder, model_name)

    def __fit(self, model_name: str, params: str):

        trainer = self.__get_trainer(model_name, params)

        self.__parse_and_validate_params(model_name, params)

        if self.is_restart:
            checkpoint_path = os.path.join(self.save_path, "checkpoints", "last.ckpt")
            trainer.fit(ckpt_path=checkpoint_path)
        else:
            trainer.fit()

    def train(self, model_name: str, experiment_name: str = "default"):
        # assert io.experiment_exists(
        #    self.root_folder, model_name, parameters
        # ), f'Experiment "{model_name}" does not exist.'
        io.assert_experiment_exists(self.root_folder, model_name, experiment_name)

        # we need to load hyperparameters before training to set save_path
        _ = self.__read_hyperparameters(model_name, experiment_name)
        self.__set_save_path(model_name, experiment_name)

        checkpoint_path = os.path.join(self.save_path, "checkpoints")
        if not os.path.exists(checkpoint_path):
            os.mkdir(checkpoint_path)
        checkpoints = [
            os.path.join(checkpoint_path, p) for p in os.listdir(checkpoint_path)
        ]
        action = "go"
        if len(checkpoints) > 0:
            while action not in ("y", "n", ""):
                action = input(
                    "Checkpiont file exists. Re-training will erase it. Continue? ([y]/n)\n"
                )
            if action in ("y", "", "Y"):
                for checkpoint in checkpoints:
                    os.remove(checkpoint)  # remove all checkpoint files
            else:
                print("Ok, exiting.")
                return

        self.__fit(model_name, experiment_name)

    def test(self, model_name: str, params: str):
        assert model_name in self.models, f'Model "{model_name}" does not exist.'
        params = "parameters" if params == "" or params == "None" else params
        print(f"Testing model {model_name} with hyperparameters: {params}.json")

        trainer = self.__get_trainer(model_name, params)

        checkpoint_path = os.path.join(self.save_path, "checkpoint", "best.ckpt")

        trainer.test(ckpt_path=checkpoint_path)

    def restart(self, model_name: str, params: str = "default"):
        # assert io.experiment_exists(
        #    self.root_folder, model_name, params
        # ), f'Model "{model_name}" does not exist.'
        io.assert_experiment_exists(self.root_folder, model_name, params)

        self.is_restart = True
        self.__fit(model_name, params)

    def tune(self, model: str, params: tuple[str, ...]):
        """
        Fine tunes specified hyperparameters. (Not implemented yet)
        """
        pass

    def generate(self, model_name: str, params: str):
        pass

    def sample(self, model_name: str, params: str):
        pass

    def install(self, source: str, destination: str):
        """
        Adds a dependency to a model.
        """
        io.install(self.root_folder, source, destination)

    def exec(self, model: str, params: str, exec_file: str):
        params = "parameters" if params == "" or params == "None" else params
        print(f"Executing model {model} with result of: {params}")
        _, model, _ = self.__get_trainer(model, params)

        self.__load_exec_function(exec_file)(model)

    def export(self):
        models = self.config.models
        for model in models:
            params = self.__populate_model_params(model)
            model["params"] = params
        # save params to mate.json
        with open("mate.json", "w") as f:
            json.dump(self.config, f, indent=4)

        print("Exported models to mate.json")

    def __export_model(self, model: str):
        export_root = os.path.join(self.root_folder, "export")

        pass

    def __populate_model_params(self, model: dict):
        export_root = self.config.export
        model = Bunch(model)

        model_class = __import__(
            f"{export_root}.{model.file}", fromlist=[model.file]
        ).__getattribute__(model.class_name)
        params = utils.get_function_parameters(model_class.__init__)

        # convert type class to strings
        for param in params:
            if isinstance(params[param], type):
                params[param] = str(params[param])

        return params
