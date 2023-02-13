import os
import traceback
from yerbamate.api.data.sources.local import io
import json
from yerbamate.api.mate_api import MateAPI

import sys

import ipdb
from .utils import utils
import shutil
from typing import Optional

from .mate_config import MateConfig


class Mate:
    """
    Mate, your friendly ML project manager.
    """

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
        """
        Initializes a new project.
        This will create the following structure:
        ```
        /
        |-- models/
        |   |-- __init__.py
        |-- experiments/
        |   |-- __init__.py
        |-- trainers/
        |   |-- __init__.py
        |-- data/
        |   |-- __init__.py
        ```

        Args:
            project_name: Name of the project.

        Example:

            `mate init my_project`

        """
        MateAPI.init_project(project_name, *args, **kwargs)

    def export(self):
        """
        Generates requirements.txt and dependencies.json files for sharing and reproducibility.

        Example:
            `mate export`
        """
        self.api.auto("export")

    def list(
        self,
        module_name: str = None,
        output_json: bool = True,
    ):
        """
        Lists all available modules.
        module_name: models, experiments, trainers, data
        """

        li = self.api.list(module_name)
        if output_json:
            print(json.dumps(li, indent=4))
        else:
            print(li)

    def auto(self, command: str):
        """
        Various commands to help with the development process.

        - `export`: Creates a requirements.txt and dependencies.json files for sharing and reproducibility.
        - `init`: Automatically creates `__init__.py` files in the project structure.

        Example:


            `mate auto export`


            `mate auto init`
        """
        self.api.auto(command)

    def summary(self, output_json: bool = True):
        """
        Prints a summary of the project modules.
        """

        print(json.dumps(self.api.summary(), indent=4))

    def clone(self, module: str, name: str, dest: str):

        # check if module exists
        module_path = os.path.join(self.root_folder, module, name)
        if not os.path.exists(module_path):
            print(f"Module {module}/{name} does not exist")
            sys.exit(1)

        # check if destination exists
        dest_path = os.path.join(self.root_folder, module, dest)
        if os.path.exists(dest_path):
            print(f"Destination {dest} exists")
            # ask if overwrite
            overwrite = input("Overwrite? (y/n): ")
            if overwrite == "y":
                shutil.rmtree(dest_path)
            else:
                sys.exit(1)
        else:
            os.makedirs(dest_path)
        # copy module to destination
        shutil.copytree(module_path, dest_path)

        print(f"Module {module}/{name} cloned to {dest}")

    def snapshot(self, model_name: str):
        pass

    def train(self, exp_module: str, exp: str, *args, **kwargs):
        """
        Runs an experiment.

        Args:

            exp_module: Name of the module where the experiment is located.

            exp: Name of the experiment.

        Example:
            `
            mate train experiments my_experiment`

        This will run the experiment `my_experiment` located in the `experiments` module.
        Equivalent to `python -m experiments.my_experiment`
        """

        # ipdb.set_trace()
        module = [self.config.project, "experiments", exp_module, exp]
        module = ".".join(module)

        try:
            __import__(module)
        except Exception as e:
            print(f"Error in loading {exp_module}/{exp}")
            print("Available experiments:")
            self.list("experiments")
            traceback.print_exc()

            # print(e)
            sys.exit(1)

    def install(self, url: str, *args, **kwargs):
        """
        Intalls a module from a git repository.

        Usage: ``mate install {url} -{y|n|o} {pm}``

        Install module support the following formats:
        - ``mate install {complete_url}``
        - ``mate install {user}/{repo}/{root_module}/{module}``
        - ``mate install {user}/{repo|root_module}/{module}``

        Args:
        -    url: Url of the git repository.
        -    -y: Skips confirmation and installs python dependencies
        -    -n: Skips installing python dependencies
        -    -o: Overwrites existing module
        -    pm: Package manager to use. Defaults to asking the user.

        Example Installing a module from structured git repository (recommended):
            

            `mate install oalee/deep-vision/deepnet/models/torch_vit -yo pip`

            This will install the module `torch_vit` from the repository `oalee/deep-vision` in to your `models` folder.
            The `yo` flags will skip confirmation and install python dependencies using pip.

        Example Installing a module from unstructured git repository:
            
            
            `mate install https://github.com/rwightman/pytorch-image-models/tree/main/timm`


            This will install the module `timm` from the repository as a sister module to your root module.
            Take into account that this will install only the code and not the python dependencies.
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
