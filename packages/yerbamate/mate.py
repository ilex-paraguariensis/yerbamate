import os
from yerbamate.api.data.sources.local import io
import json
from yerbamate.api.mate_api import MateAPI

import sys

from .trainers.trainer import Trainer
import ipdb
from .utils import utils


from typing import Optional

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

        self.api = MateAPI(self.config)
        self.is_restart = False
        self.run_params = None
        self.custom_save_path = None
        # ipdb.set_trace()

    @staticmethod
    def init(project_name: str):

        MateAPI.init_project(project_name)
        # self.__findroot()
        # self.models = self.__list_packages("models")
        # self.api = MateAPI(self.config)

    def export(self):
        self.api.auto("export")

    def list(
        self, module_name: str, query: Optional[str] = None, output_json: bool = True
    ):
        li = self.api.list(module_name, query)
        if output_json:
            print(json.dumps(li, indent=4))
        else:
            print(li)

    """
        auto init -> creates __init__.py recursively
        auto export -> creates requirements.txt for export
    """

    def auto(self, command: str):
        self.api.auto(command)

    def summary(self, output_json: bool = True):
        print(json.dumps(self.api.summary(), indent=4))

    def clone(self, source_model: str, target_model: str):
        pass

    def snapshot(self, model_name: str):
        pass

    def train(self, experiment_name: str = "default"):

        self.api.select_experiment(experiment_name)
        self.api.train()

    def metadata(
        self,
    ):
        self.api.generate_metadata(True)

    def test(self, experiment_name: str):
        """
        TODO: Implement test in trainer
        """
        # assert model_name in self.models, f'Model "{model_name}" does not exist.'
        # params = "parameters" if params == "" or params == "None" else params
        # print(f"Testing model {model_name} with hyperparameters: {params}.json")

        # trainer = self.__get_trainer(model_name, params)

        # checkpoint_path = os.path.join(self.save_path, "checkpoint", "best.ckpt")

        # trainer.test(ckpt_path=checkpoint_path)
        self.api.select_experiment(experiment_name)
        self.api.test()

    def restart(self, model_name: str, params: str = "default"):
        """
        TODO: Implement restart in trainer
        """
        pass
        # assert io.experiment_exists(
        #    self.root_folder, model_name, params
        # ), f'Model "{model_name}" does not exist.'
        # io.assert_experiment_exists(self.root_folder, model_name, params)

        # self.is_restart = True
        # self.__fit(model_name, params)

    def tune(self, model: str, params: tuple[str, ...]):
        """
        Fine tunes specified hyperparameters. (Not implemented yet)
        """
        pass

    def generate(self, model_name: str, params: str):
        pass

    def sample(self, model_name: str, params: str):
        pass

    def install(self, url: str):
        """
        Adds a dependency to a model.
        """
        self.api.install_url(url)

    def exec(self, model: str, params: str, exec_file: str):
        params = "parameters" if params == "" or params == "None" else params
        print(f"Executing model {model} with result of: {params}")
        _, model, _ = self.__get_trainer(model, params)

        self.__load_exec_function(exec_file)(model)

    def board(self):

        self.api.start_mateboard()

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
