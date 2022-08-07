from curses.panel import new_panel
import os
from argparse import ArgumentParser
import importlib
from pytorch_lightning import LightningModule, Trainer
import pytorch_lightning as pl
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint

from .bunch import Bunch
from .migrator import Migration
from torch import nn
import torch as t
import ipdb
import json
import sys
import importlib
import pkgutil
import shutil
from glob import glob
from .logger import CustomLogger
import mate
from .utils import get_model_parameters, get_function_parameters
from . import __version__


class Mate:
    def __init__(self):
        self.root_folder = ""
        self.save_path = ""
        self.current_folder = os.path.dirname(__file__)
        self.__findroot()
        self.models = self.__list_packages("models")
        self.is_restart = False
        self.run_params = None
        self.custom_save_path = None

    def __list_packages(self, folder: str):
        return (
            tuple(
                x
                for x in os.listdir(os.path.join(self.root_folder, folder))
                if not "__" in x
            )
            if os.path.exists(os.path.join(self.root_folder, folder))
            else tuple()
        )

    def __handle_mate_version(self, path: str):
        if not self.config.contains("mate_version"):
            self.config.mate_version = "0.2.4"  # TODO: change this to __version__
            with open(path, "w") as f:
                json.dump(self.config, f, indent=4)

        if self.config.mate_version != __version__:
            print(
                f"New mate version has been installed. Going to handle migration from {self.config.mate_version} to {__version__}"
            )
            migrator = Migration(
                self.root_folder, self.config.mate_version, __version__
            )
            success = migrator.migrate()
            if not success:
                print(
                    "Migration failed... please check the logs and make an issue on github"
                )
                # sys.exit(1)
            else:
                self.config.mate_version = __version__
                with open(path, "w") as f:
                    json.dump(self.config, f, indent=4)
                print("Migration successful")

    def __load_mate_config(self, path):
        with open(path) as f:
            self.config = Bunch(json.load(f))
            assert (
                "results_folder" in self.config
            ), 'Please add "results_folder":<path> in mate.json'
            assert (
                "project" in self.config
            ), 'Please add "project":<project name> in mate.json'

    def __findroot(self):
        """
        Method in charge of finding the root folder of the project and reading the content of mate.json
        """
        # path of execution
        current_path = os.getcwd()
        found = False
        i = 0
        while not found and i < 6:

            if os.path.exists(os.path.join(current_path, "mate.json")):
                conf_path = os.path.join(current_path, "mate.json")
                self.__load_mate_config(conf_path)
                self.root_folder = self.config.project
                # self.__import_submodules(self.root_folder)
                found = True
                self.root_save_folder = self.config.results_folder
            else:
                os.chdir("..")
                current_path = os.getcwd()
                i += 1
                if current_path == "/" or i == 6:
                    print("Could not find mate.json")
                    sys.exit(1)

        # self.root_save_folder = self.root_folder
        sys.path.insert(0, os.getcwd())
        self.__handle_mate_version(conf_path)

    def __load_lightning_class(
        self, model_name: str, params: Bunch, parameters_file_name: str
    ) -> LightningModule:
        model = __import__(
            f"{self.root_folder}.models.{model_name}.{params.train}",
            fromlist=["models"],
        ).Model(params)
        for m in params.model.keys():
            torch_model = self.__load_torch_model_class(
                model_name, params, m, parameters_file_name
            )
            model.__setattr__(m, torch_model)

        return model

    def __load_torch_model_class(
        self,
        model_name,
        params: Bunch,
        internal_model_name: str,
        parameters_file_name: str,
    ):
        conf = Bunch(
            params.model[internal_model_name]
        )  # TODO, bunch does not work for nested dicts
        module = __import__(
            f"{self.root_folder}.models.{model_name}.{conf['folder']}",
            fromlist=[conf["folder"].split(".")[-1]],
        )
        model_class = getattr(module, conf["class"])
        if conf.contains("params"):
            model = model_class(**dict(conf.params))
        else:
            print(
                f"No parameters found for model {model_class}, using default ones. They will be added to the hyperparameters file."
            )
            model = model_class()

            # populate and save parameters
            model_params = get_function_parameters(model.__init__)
            # convert type class to strings
            for param in model_params:
                if isinstance(model_params[param], type):
                    model_params[param] = str(model_params[param])

            # idk why but without this the parameters are not saved, some bug in Bunch class
            conf["params"] = model_params
            params.model[internal_model_name] = conf
            params["model"] = params.model

            # save parameters
            hparams_source_file_name = os.path.join(
                self.root_folder,
                "models",
                model_name,
                "hyperparameters",
                f"{parameters_file_name}.json",
            )

            hparams = Bunch(json.loads(json.dumps(params)))
            with open(hparams_source_file_name, "w") as f:
                json.dump(hparams, f, indent=4)

        return model

    def __load_logger_class(self):
        return CustomLogger

    def __load_data_loader_class(self, data_loader_name: str):
        data_class = f"{self.root_folder}.data_loaders.{data_loader_name}.data_loader"
        return __import__(
            f"{data_class}",
            fromlist=["data_loader"],
        ).CustomDataModule

    def __load_exec_function(self, exec_file: str):
        return __import__(
            f"{self.root_folder}.exec.{exec_file}",
            fromlist=["exec"],
        ).run

    def __set_save_path(self, model_name: str, params: str):
        self.save_path = os.path.join(
            self.root_save_folder, "models", model_name, "results", params
        )
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        # save parameters in results folder
        hparams_source_file_name = os.path.join(
            self.root_folder,
            "models",
            model_name,
            "hyperparameters",
            f"{params}.json",
        )
        hparams_destination_file_name = os.path.join(
            self.save_path, "train_parameters.json"
        )
        shutil.copy(hparams_source_file_name, hparams_destination_file_name)

    def __override_run_params(self, params: Bunch):
        if self.run_params == None:
            return params
        for key, value in self.run_params.items():
            # nested parameters
            if "." in key:
                len_subs = len(key.split("."))
                if len_subs == 2:
                    params[key.split(".")[0]][key.split(".")[1]] = value
                elif len_subs == 3:
                    params[key.split(".")[0]][key.split(".")[1]][
                        key.split(".")[2]
                    ] = value
                elif len_subs == 4:
                    params[key.split(".")[0]][key.split(".")[1]][key.split(".")[2]][
                        key.split(".")[3]
                    ] = value
                elif len_subs == 5:
                    params[key.split(".")[0]][key.split(".")[1]][key.split(".")[2]][
                        key.split(".")[3]
                    ][key.split(".")[4]] = value
                # for now we only support 5 levels of nesting
            else:
                params[key] = value
        return params

    def __override_params(self, params: Bunch):
        if "override_params" in self.config and self.config.override_params.enabled:
            for key, value in self.config.override_params.items():
                if key == "enabled":
                    key = "override_params"
                params[key] = value
        return params

    def __move_results_in_wrong_location(self, model_name: str, params: str):
        possibly_wrong_save_path = os.path.join(
            self.root_folder, "models", model_name, "results", params
        )
        if self.root_folder != self.root_save_folder and os.path.exists(
            possibly_wrong_save_path
        ):
            print(
                f"Found results in wrong location: {possibly_wrong_save_path}\nMoving them to the correct one."
            )
            os.system(f"mv {possibly_wrong_save_path} {self.save_path}")

    def __read_hyperparameters(self, model_name: str, hparams_name: str = "default"):
        with open(
            os.path.join(
                self.root_folder,
                "models",
                model_name,
                "hyperparameters",
                f"{hparams_name}.json",
            )
        ) as f:
            hparams = json.load(f)
        env_location = os.path.join(
            self.root_folder,
            "env.json",
        )
        if not os.path.exists(env_location):
            print(f"Could not find env.json in {env_location}. Created one.")
            with open(env_location, "w") as f:
                json.dump({}, f)

        with open(env_location) as f:
            env = json.load(f)

        env_in_params = [
            (key, val) for key, val in hparams.items() if key.startswith("env.")
        ]
        modified_env = False
        for key, val in env_in_params:
            stripped_key = key[4:]
            if key not in env:
                env[stripped_key] = val
                modified_env = True
            hparams[stripped_key] = env[stripped_key]
            hparams.pop(key, None)

        if modified_env:
            with open(env_location, "w") as f:
                json.dump(env, f, indent=4)
            print("Updated env.json")
            print(json.dumps(env, indent=4))

        hparams = Bunch(hparams)
        hparams = self.__override_params(hparams)
        hparams = self.__override_run_params(hparams)
        print(json.dumps(hparams, indent=4))
        # trick to save parameters, otherwise changes are not saved after return!
        hparams = Bunch(json.loads(json.dumps(hparams)))
        self.__move_results_in_wrong_location(model_name, hparams_name)
        return hparams

    def __get_trainer(self, model_name: str, parameters: str):
        params = self.__read_hyperparameters(model_name, parameters)
        self.__set_save_path(model_name, parameters)
        params.save_path = self.save_path
        model = self.__load_lightning_class(model_name, params, parameters)
        data_module = self.__load_data_loader_class(params.data_loader)(params)
        logger_module = self.__load_logger_class()
        params.model_name = model_name

        if self.config.contains("print_model"):
            if self.config.print_model:
                print(model)

        checkpoint_path = os.path.join(self.save_path, "checkpoint")
        checkpoint_file = os.path.join(checkpoint_path, "last.ckpt")
        if os.path.exists(checkpoint_file):
            print(f"Loaded model from {checkpoint_file}")
            # model.load_state_dict(t.load(checkpoint_file))
            model.load_from_checkpoint(checkpoint_file, params=params, strict=False)
            # model.params = params

        callbacks = []
        if params.contains("model_checkpoint"):
            model_saver_callback = ModelCheckpoint(
                checkpoint_path,
                filename="best",
                **dict(params.model_checkpoint),
            )
            callbacks.append(model_saver_callback)

        if params.contains("early_stopping"):
            callbacks.append(EarlyStopping(**params.early_stopping))

        # monitor = mate.OptimizerMonitor(params, "epoch")
        # callbacks.append(monitor)

        trainer = Trainer(
            max_epochs=params.max_epochs,
            gpus=(1 if params.cuda else None),
            callbacks=callbacks,
            logger=logger_module(params),
            enable_checkpointing=True,
        )
        return (trainer, model, data_module)

    def init(self, results_folder: str):
        os.system("git clone https://github.com/ilex-paraguariensis/init-mate-project")
        shutil.rmtree("init-mate-project/.git")
        os.rename("init-mate-project/*", ".")  # TODO: not sure this works
        # TODO: add results_folder to mate.json
        # TODO: write mate.json

    def create(self, path: str):
        pass

    def remove(self, model_name: str):
        action = "go"
        while action not in ("y", "n"):
            action = input(
                f'Are you sure you want to remove model "{model_name}"? (y/n)\n'
            )
        if action == "y":
            shutil.rmtree(os.path.join(self.root_folder, "models", model_name))
            print(f"Removed model {model_name}")
        else:
            print("Ok, exiting.")

    def list(self, folder: str):
        print("\n".join(tuple("\t" + str(m) for m in self.__list_packages(folder))))

    def clone(self, source_model: str, target_model: str):
        shutil.copytree(
            os.path.join(self.root_folder, "models", source_model),
            os.path.join(self.root_folder, "models", target_model),
        )

    def snapshot(self, model_name: str):

        if not os.path.exists(os.path.join(self.root_folder, "snapshots")):
            os.makedirs(os.path.join(self.root_folder, "snapshots"))

        snapshot_names = [
            name.split("__")
            for name in os.listdir(os.path.join(self.root_folder, "snapshots"))
        ]
        matching_snapshots = [name for name in snapshot_names if name[0] == model_name]
        max_version_matching = (
            max([int(name[1]) for name in matching_snapshots])
            if len(matching_snapshots) > 0
            else 0
        )
        snapshot_name = f"{model_name}__{max_version_matching + 1}"

        shutil.copytree(
            os.path.join(self.root_folder, "models", model_name),
            os.path.join(self.root_folder, "snapshots", snapshot_name),
        )
        print(f"Created snapshot {snapshot_name}")

    def __fit(self, model_name: str, params: str):
        trainer, model, data_module = self.__get_trainer(model_name, params)

        if self.is_restart:
            checkpoint_path = os.path.join(self.save_path, "checkpoint", "last.ckpt")
            trainer.fit(model, datamodule=data_module, ckpt_path=checkpoint_path)
        else:
            trainer.fit(model, datamodule=data_module)
        # trainer.fit(model, datamodule=data_module)

    def train(self, model_name: str, parameters: str = "default"):
        assert model_name in self.models, f'Model "{model_name}" does not exist.'
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
        new_parameters = get_model_parameters(
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
        params = get_function_parameters(model_class.__init__)

        # convert type class to strings
        for param in params:
            if isinstance(params[param], type):
                params[param] = str(params[param])

        return params

    """ Import all submodules of a module, recursively, including subpackages
    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    def __import_submodules(self, package, recursive=True):
        # print(os.getcwd())
        if isinstance(package, str):
            package = importlib.import_module(package)
        results = {}
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
            full_name = package.__name__ + "." + name
            results[full_name] = importlib.import_module(full_name)
            if recursive and is_pkg:
                results.update(self.__import_submodules(full_name))
        return results
    """
