import os
from yerbamate.api.data.sources.local import io
import json
from yerbamate.api.mate_api import MateAPI

import sys

import ipdb
from .utils import utils

from typing import Optional

from .mate_config import MateConfig



class Mate:


    def __init__(self, init=False):
        self.root_folder = ""
        self.save_path = ""
        self.current_folder = os.path.dirname(__file__)
        self.config: Optional[MateConfig] = None
        self.__findroot()
        self.api = MateAPI(self.config)
        self.run_params = None

 
    @staticmethod
    def init(project_name: str, *args, **kwargs):
        MateAPI.init_project(project_name, *args, **kwargs)
 

    def export(self):
        self.api.auto("export")

    def list(
        self,
        module_name: str = None,
        output_json: bool = True,
    ):
        li = self.api.list(module_name)
        if output_json:
            print(json.dumps(li, indent=4))
        else:
            print(li)


    def auto(self, command: str):
        """
        auto init -> creates __init__.py recursively
        auto export -> creates requirements.txt for export
        """
        self.api.auto(command)


    def summary(self, output_json: bool = True):
        print(json.dumps(self.api.summary(), indent=4))

    def clone(self, source_model: str, target_model: str):
        pass

    def snapshot(self, model_name: str):
        pass

    def train(self, model: str, exp: str , *args, **kwargs):
        # ipdb.set_trace()
        module = [self.config.project, "experiments", model, exp]
        module = ".".join(module)

        try:
            __import__(module)
        except Exception as e:
            print(f"Error in loading {model}/{exp}")
            print(e)
            print("Available experiments:")
            self.list("experiments")
            sys.exit(1)



    def install(self, url: str, *args, **kwargs):
        """
        Adds a dependency to a model.
        """
        self.api.install_url(url, *args, **kwargs)

    def exec(self, model: str, params: str, exec_file: str):
        params = "parameters" if params == "" or params == "None" else params
        print(f"Executing model {model} with result of: {params}")
        _, model, _ = self.__get_trainer(model, params)

        self.__load_exec_function(exec_file)(model)

    # def board(self):

    #     self.api.start_mateboard()

    # def __list_packages(self, folder: str):
    #     return io.list_packages(self.root_folder, folder)

    # def __update_mate_version(self):
    #     utils.migrate_mate_version(self.config, self.root_folder)

    def __findroot(self):
        """
        Method in charge of finding the root folder of the project and reading the content of mate.json
        """
        self.root_folder, self.config = io.find_root()
        self.root_save_folder = self.config.results_folder

    # def __get_trainer(self, params: str):
    #     if self.trainer is None:

    #         conf, save_path = self.package_manager.load_experiment(params)

    #         print(conf)

    #         map_key_value = {
    #             "save_path": self.save_path,
    #             "save_dir": self.save_path,
    #         }
    #         root_module = f"{self.root_folder}"

    #         self.trainer = Trainer.create(conf, root_module, map_key_value)

    #     return self.trainer

    # def __fit(self, params: str):

    #     trainer = self.__get_trainer(params)

    #     self.__parse_and_validate_params(params)

    #     if self.is_restart:
    #         checkpoint_path = os.path.join(self.save_path, "checkpoints", "last.ckpt")
    #         trainer.fit(ckpt_path=checkpoint_path)
    #     else:
    #         trainer.fit()
