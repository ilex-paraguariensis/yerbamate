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



class Mate:
    """
    Mate, your friendly ML project manager.
    """

    def __init__(self, init=False):
        self.root_folder = ""
        self.save_path = ""
        self.current_folder = os.path.dirname(__file__)
        self.config = None
        self.__findroot()
        self.api = MateAPI(self.config)
        self.run_params = None

    @staticmethod
    def init(project_name: str, *args, **kwargs):
        """

        `mate init {project_name}`

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
        Generates requirements.txt, dependencies.json and exports.md for sharing and reproducibility.

        Example:
            `mate export`

        Output:
            ```
            Generated requirements.txt for gan/models/lgan
            Generated dependencies.json for gan/experiments/lwgan
            Generated requirements.txt for gan/experiments/lwgan
            Generated requirements.txt for gan/trainers/lgan
            Generated requirements.txt for gan/data/cars
            Exported to export.md
            ```
        
        """
        self.api.auto("export")

    def list(
        self,
        module_name: str = None,
        output_json: bool = True,
    ):
        """


        Lists all available modules.

        Args:
            module_name: Name of the module to list. If not specified, all modules will be listed.

        Examples:
            `mate list models`

            `mate list`

        """

        li = self.api.list(module_name)
        if output_json:
            print(json.dumps(li, indent=4))
        else:
            print(li)

    def auto(self, command: str):
        """

        `mate auto {command}`

        Various commands to help with the development process.


        commands:
        - `export`: Creates a requirements.txt and dependencies.json files for sharing and reproducibility.
        - `init`: Automatically creates `__init__.py` files in the project structure.

        Example:


            `mate auto export`
            `mate auto init`
        """
        self.api.auto(command)

    def summary(self):
        """
        Prints a summary of the project modules. Same as `mate list`
        """

        print(json.dumps(self.api.summary(), indent=4))

    def clone(self, module: str, name: str, dest: str, *args, **kwargs):
        """
        `mate clone {module} {name} {dest} {-o}`

        Clones a source code module to a new destination.

        Args:

            module: Module to clone.

            name: Name of the module to clone.

            dest: Destination to clone the module to.

            -o: Overwrite destination if it exists.

        Example:

            `mate clone models torch_vit my_vit`
        """

        # check if module exists
        module_path = os.path.join(self.root_folder, module, name)
        if not os.path.exists(module_path):
            print(f"Module {module}/{name} does not exist")
            sys.exit(1)

        # check if destination exists
        dest_path = os.path.join(self.root_folder, module, dest)
        if os.path.exists(dest_path):

            if "-o" in args:
                shutil.rmtree(dest_path)
                print(f"Removed {dest_path}")
            else:
                print(f"Destination {dest} exists")
                overwrite = input("Overwrite? (y/n): ")
                if overwrite == "y":
                    shutil.rmtree(dest_path)
                    print(f"Removed {dest_path}")
                else:
                    sys.exit(1)

        # copy module to destination
        shutil.copytree(module_path, dest_path)

        print(f"Module {module}/{name} cloned to {dest_path}")

    def snapshot(self, model_name: str):
        pass

    def data(self, base_module, sub_module):

        module = [self.config.project, 'data', base_module, sub_module]
        module = ".".join(module)

        try:
            __import__(module)
        except Exception as e:
            print(f"Error in loading {base_module}/{sub_module}")
            print("Available experiments:")
            self.list(base_module)
            traceback.print_exc()

            # print(e)
            sys.exit(1)



    def train(self, exp_module: str, exp: str, *args, **kwargs):
        """
        Executes an experiment.

        Usage: ``mate train {module} {experiment}``

        Args:

            exp_module: Name of the module where the experiment is located.

            exp: Name of the experiment.

        Example:
            `
            mate train experiments my_experiment`

        This will run the experiment `my_experiment` located in the `experiments` module.

        Equivalent to `python -m root_module.experiments.my_experiment train`
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

    def test(self, exp_module: str, exp: str, *args, **kwargs):
        """
        Executes an experiment.

        Usage: ``mate test {module} {experiment}``

        Args:

            exp_module: Name of the module where the experiment is located.

            exp: Name of the experiment.

        Example:
            `
            mate test experiments my_experiment`

        This will run the experiment `my_experiment` located in the `experiments` module.

        Equivalent to `python -m root_module.experiments.my_experiment test`
        """
        self.train(exp_module, exp, *args, **kwargs)

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
        -    -o: Overwrites existing code modules
        -    pm: Package manager to use. Defaults to asking the user.

        Example Installing a module from structured git repository (recommended):


            mate install oalee/deep-vision/deepnet/models/torch_vit -yo pip

            This will install the module `torch_vit` from the repository `oalee/deep-vision` in to your `models` folder.
            The `yo` flags will skip confirmation and install python dependencies using pip.

        Example Installing a module from unstructured git repository:


            mate install https://github.com/rwightman/pytorch-image-models/tree/main/timm


            This will install the module `timm` from the repository as a sister module to your root module.
            Take into account that this will install only the code and not the python dependencies.
        """
        self.api.install_url(url, *args, **kwargs)

    def __findroot(self):
        """
        Method in charge of finding the root folder of the project and reading the content of mate.json
        """
        self.root_folder, self.config = io.find_root()
        # self.root_save_folder = self.config.results
