from curses.panel import new_panel
import os
from argparse import ArgumentParser, Namespace

from sre_constants import ASSERT
from pytorch_lightning import LightningModule, Trainer


from yerbamate.bunch import Bunch
from yerbamate.migrator import Migration


import ipdb
import json
import sys

import shutil


from yerbamate import utils, parser, io, package


class Mate:
    @staticmethod
    def init(project_name: str):
        # should actually be a package install
        pass

    def __init__(self, init=False):
        self.root_folder = ""
        self.save_path = ""
        self.current_folder = os.path.dirname(__file__)
        self.__findroot()
        self.__update_mate_version()
        self.models = self.__list_packages("models")
        self.is_restart = False
        self.run_params = None
        self.custom_save_path = None

    def __list_packages(self, folder: str):
        return io.list_packages(self.root_folder, folder)

    def experiments(self, model_name: str = None):
        io.experiments(self.root_folder, model_name)

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

        root_module = f"{self.root_folder}"
        base_module = f"{self.root_folder}.models.{model_name}"

        parsed_params, errors = parser.generate_params(
            root, base_module, root_module, generate_defaults
        )

        if len(errors) > 0:
            print(f"Errors in {model_name}/{experiment}")
            for error in errors:
                print(error)

            io.update_hyperparameters(
                self.root_folder, model_name, experiment, parsed_params
            )
            sys.exit(1)

        return parsed_params

    def __load_pl_trainer_package(
        self, params: Bunch, model_name: str, experiment: str, map_key_values: dict = {}
    ):

        pl_package_params = Bunch({})
        pl_package_params.params = params.clone()

        module_class = package.PLTrainerPackage
        trainer_package = module_class(**pl_package_params)

        map_key_values.update({"save_path": self.save_path, "save_dir": self.save_path})

        return trainer_package.install_objects(
            self.root_folder, f"{self.root_folder}.models.{model_name}", map_key_values
        )

    def __load_exec_function(self, exec_file: str):
        return __import__(
            f"{self.root_folder}.exec.{exec_file}",
            fromlist=["exec"],
        ).run

    def __set_save_path(self, model_name: str, params: str):
        self.save_path = io.set_save_path(
            self.root_save_folder, self.root_folder, model_name, params
        )

    def __read_hyperparameters(self, model_name: str, hparams_name: str = "default"):

        hp = io.read_hyperparameters(
            self.config, self.root_folder, model_name, hparams_name, self.run_params
        )

        # this function will exit the program if there are missing parameters
        self.__validate_missing_params(hp, model_name, hparams_name)

        # all params are now validated, we can update the whole generated file
        all_params = self.__validate_missing_params(
            hp, model_name, hparams_name, generate_defaults=True
        )

        io.save_train_hyperparameters(self.save_path, all_params, self.config)

        return hp

    def __get_trainer(self, model_name: str, parameters: str):
        params = self.__read_hyperparameters(model_name, parameters)
        self.__set_save_path(model_name, parameters)
        params.save_path = self.save_path

        print(params)

        objects = self.__load_pl_trainer_package(params, model_name, parameters)

        if self.config.contains("print_model"):
            if self.config.print_model:
                print(objects["pytorch_lightning_module"])
        return (
            objects["trainer"],
            objects["pytorch_lightning_module"],
            objects["data"],
        )

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
        trainer, model, data_module = self.__get_trainer(model_name, params)

        if self.is_restart:
            checkpoint_path = os.path.join(self.save_path, "checkpoints", "last.ckpt")
            trainer.fit(model, datamodule=data_module, ckpt_path=checkpoint_path)
        else:
            trainer.fit(model, datamodule=data_module)
        # trainer.fit(model, datamodule=data_module)

    def __load_hyperparameter(self, model_name: str, params: str):

        params = self.__read_hyperparameters(model_name, params)
        self.__set_save_path(model_name, params)

    def train(self, model_name: str, parameters: str = "default"):
        assert (
            model_name in self.models or model_name
        ), f'Model "{model_name}" does not exist.'
        print(f"Training model {model_name} with hyperparameters: {parameters}.json")

        # we need to load hyperparameters before training to set save_path
        _ = self.__read_hyperparameters(model_name, parameters)
        self.__set_save_path(model_name, parameters)

        checkpoint_path = os.path.join(self.save_path, "checkpoint")
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

        self.__fit(model_name, parameters)

    def test(self, model_name: str, params: str):
        assert model_name in self.models, f'Model "{model_name}" does not exist.'
        params = "parameters" if params == "" or params == "None" else params
        print(f"Testing model {model_name} with hyperparameters: {params}.json")

        trainer, model, data_module = self.__get_trainer(model_name, params)

        checkpoint_path = os.path.join(self.save_path, "checkpoint", "best.ckpt")

        trainer.test(model, datamodule=data_module, ckpt_path=checkpoint_path)

    def restart(self, model_name: str, params: str):
        assert model_name in self.models, f'Model "{model_name}" does not exist.'
        params = "parameters" if params == "" or params == "None" else params
        print(f"Restarting model {model_name} with parameters: {params}.json")

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

    def add(self, model_name: str, repo: str):
        """
        Adds a dependency to a model.
        """
        mate_dir = ".mate"
        if not os.path.exists(mate_dir):
            os.makedirs(mate_dir, exist_ok=True)
        os.system(f"git clone {repo} {mate_dir}")

        conf = os.path.join(mate_dir, "mate.json")
        conf = Bunch(json.load(open(conf)))

        dest_dir = os.path.join(self.root_folder, "models", model_name, "modules")
        os.makedirs(dest_dir, exist_ok=True)

        shutil.copytree(os.path.join(mate_dir, conf.export), dest_dir)
        shutil.copytree(
            os.path.join(mate_dir, "mate.json"),
            os.path.join(dest_dir, conf.export),
        )
        shutil.rmtree(mate_dir)

        new_params = {}
        for model in conf.models:
            new_params[model["class_name"]] = model["params"]
        ipdb.set_trace()
        old_params_files = [
            os.path.join(self.root_folder, "models", model_name, "hyperparameters", p)
            for p in os.listdir(
                os.path.join(self.root_folder, "models", model_name, "hyperparameters")
            )
        ]
        for old_params_file in old_params_files:
            p = Bunch(json.load(open(old_params_file)))
            p.update(new_params)
            with open(old_params_file, "w") as f:
                json.dump(p, f, indent=4)
        print(f"Sucessfully added dependency to model {model_name}")

    def install(self, repo: str, source_model: str, destination_model: str):
        """
        installs a package
        """
        source_model_base_name = (
            source_model.split(".")[-1] if "." in source_model else source_model
        )
        mate_dir = ".matedir"
        if not os.path.exists(mate_dir):
            os.mkdir(mate_dir)
        os.system(f"git clone {repo} {mate_dir}")
        os.system(
            f"mv {os.path.join(mate_dir, '*')} {os.path.join(destination_model, source_model_base_name)}"
        )
        new_parameters = utils.get_model_parameters(
            os.path.join(source_model, destination_model)
        )
        old_params_files = [
            os.path.join("hyperparameters", p) for p in os.listdir("hyperparameters")
        ]
        for old_params_file in old_params_files:
            params_name = old_params_file.split(".")[0]
            old_params = self.__read_hyperparameters(destination_model, params_name)
            old_params[source_model_base_name] = new_parameters
            with open(old_params_file, "w") as f:
                json.dump(old_params, f)

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
