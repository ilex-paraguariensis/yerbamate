import os

from yerbamate.packages.package_manager import PackageManager

from .packages.metadata.generator import MetadataGenerator

from .utils.bunch import Bunch

import json
import sys

from .trainers.trainer import Trainer
import ipdb
from .utils import utils
from .packages.sources.local import io
from bombilla import parser

from typing import Optional
from .packages.package_repository import PackageRepository
from .mate_config import MateConfig
from .mateboard.mateboard import MateBoard


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
        self.models = self.__list_packages("models")
        self.is_restart = False
        self.run_params = None
        self.custom_save_path = None
        self.trainer: Optional[Trainer] = None
        assert self.config is not None
        self.package_manager = PackageManager(self.config)

    def create(self, path: str):
        pass

    def remove(self, model_name: str):
        io.remove(self.root_folder, model_name)

    def list(self, module_name: str = None, query: str = None):

        li = self.package_manager.list(module_name, query)
        print(li)

        # return print("\t" + "\n\t".join(self.data_source.get(folder)))

    def clone(self, source_model: str, target_model: str):
        io.clone(self.root_folder, source_model, target_model)

    def snapshot(self, model_name: str):
        io.snapshot(self.root_folder, model_name)

    def train(self, experiment_name: str = "default"):

        assert (
            len(self.package_manager.list("experiments", experiment_name)) > 0
        ), f'Experiment "{experiment_name}" does not exist.'

        # we need to load hyperparameters before training to set save_path
        exp, self.save_path = self.package_manager.load_experiment(experiment_name)

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

        self.__fit(experiment_name)

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

    def board(self):
        board = MateBoard()
        board.start()

    def __list_packages(self, folder: str):
        return io.list_packages(self.root_folder, folder)

    def __update_mate_version(self):
        utils.migrate_mate_version(self.config, self.root_folder)

    def __findroot(self):
        """
        Method in charge of finding the root folder of the project and reading the content of mate.json
        """
        self.root_folder, self.config = io.find_root()
        self.root_save_folder = self.config.results_folder

    def __load_exec_function(self, exec_file: str):
        return __import__(
            f"{self.root_folder}.exec.{exec_file}",
            fromlist=["exec"],
        ).run

    def __parse_and_validate_params(self, params: str):
        assert (
            self.trainer is not None
        ), "Trainer must be initialized before parsing params (Bombilla is managed by Trainer)"

        full, err = self.trainer.generate_full_dict()

        if len(err) > 0:
            print(f"Errors in {params}")
            for error in err:
                print(error)

            sys.exit(1)

        io.save_train_experiments(self.save_path, full, self.config)

        return full

    def __get_trainer(self, params: str):
        if self.trainer is None:

            conf, save_path = self.package_manager.load_experiment(params)

            print(conf)

            map_key_value = {
                "save_path": self.save_path,
                "save_dir": self.save_path,
            }
            root_module = f"{self.root_folder}"

            self.trainer = Trainer.create(conf, root_module, map_key_value)

        return self.trainer

    def __fit(self, params: str):

        trainer = self.__get_trainer(params)

        self.__parse_and_validate_params(params)

        if self.is_restart:
            checkpoint_path = os.path.join(self.save_path, "checkpoints", "last.ckpt")
            trainer.fit(ckpt_path=checkpoint_path)
        else:
            trainer.fit()
