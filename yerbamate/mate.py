import os
from argparse import ArgumentParser
import importlib
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import EarlyStopping
from .bunch import Bunch
from torch import nn
import torch as t
import ipdb
import json
import sys
import importlib
import pkgutil
from .logger import CustromLogger
import mate


class Mate:
    def __init__(self):
        self.root_folder = ""
        self.save_path = ""
        self.current_folder = os.path.dirname(__file__)
        self.__findroot()
        self.models = self.__list_packages("models")
        self.is_restart = False

    def __init_cache(self):
        self.cache = mate.Cache(self.save_path)

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

    def __load_mate_config(self, path):
        with open(path) as f:
            self.config = Bunch(json.load(f))

    def __findroot(self):
        # directory of yerbamate
        current_dir = os.path.dirname(os.path.realpath(__file__))
        cur_folder = os.path.dirname(__file__)

        # path of execution
        current_path = os.getcwd()

        if not os.path.exists(os.path.join(current_path, "mate.json")):
            self.root_folder = os.path.basename(current_path)
            os.chdir("..")
            self.__load_mate_config(os.path.join(os.getcwd(), "mate.json"))
        else:
            self.__load_mate_config(os.path.join(current_path, "mate.json"))
            self.root_folder = os.path.basename(
                os.path.join(current_path, self.config.project)
            )

        sys.path.insert(0, os.getcwd())

    def __load_model_class(self, model_name: str, folder="models"):
        # print(sys.meta_path)
        return __import__(
            f"{self.root_folder}.{folder}.{model_name}.model",
            fromlist=[folder],
        ).Model

    def __load_logger_class(self):
        return CustromLogger

    def __load_data_loader_class(self, data_loader_name: str):
        data_class = f"{self.root_folder}.data_loaders.{data_loader_name}.data_loader"
        return __import__(
            f"{data_class}",
            fromlist=["data_loader"],
        ).CustomDataModule

    def __set_save_path(self, model_name: str, params: str):
        self.save_path = os.path.join(
            self.root_folder, "models", model_name, "results", params
        )
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        # save parameters in results folder
        os.system(
            f"cp {os.path.join(self.root_folder, 'models', model_name, 'hyperparameters' , f'{params}.json')} {os.path.join(self.save_path, 'train_parameters.json')}"
        )
        self.__init_cache()

    def __override_params(self, params: Bunch):
        if "override_params" in self.config and self.config.override_params.enabled:
            for key, value in self.config.override_params.items():
                if key == "enabled":
                    key = "override_params"
                params[key] = value
        return params

    def __reload_lr_from_cache(self, params: Bunch):
        if not self.is_restart:
            return params
        params["restarted"] = True
        try:
            lr = self.cache.get("lr", None)["lr-Adam"]
            if lr != params.optimizer.lr:
                optimizer = params.optimizer
                optimizer.lr = lr
                params.optimizer = optimizer
                print(f"Reloaded learning rate to {lr}")
                return params
            return params
        except:
            return params

    def __read_hyperparameters(self, model_name: str, params: str = "default"):
        with open(
            os.path.join(
                self.root_folder,
                "models",
                model_name,
                "hyperparameters",
                f"{params}.json",
            )
        ) as f:
            params = json.load(f)
        params = Bunch(params)
        params = self.__reload_lr_from_cache(params)
        params = self.__override_params(params)
        print(json.dumps(params, indent=4))
        return params

    def __get_trainer(self, model_name: str, params: str):
        self.__set_save_path(model_name, params)
        params = self.__read_hyperparameters(model_name, params)
        params.save_path = self.save_path
        model = self.__load_model_class(model_name)(params)
        # print(model)
        data_module = self.__load_data_loader_class(params.data_loader)(params)
        logger_module = self.__load_logger_class()
        params.model = model_name

        checkpoint_path = os.path.join(self.save_path, "model.pt")
        if os.path.exists(checkpoint_path):
            print(f"Loaded model from {checkpoint_path}")
            model.load_state_dict(t.load(checkpoint_path))

        # TODO assert that optimizer is in params
        callbacks = []
        if params.contains("optimizer"):
            if params.optimizer.contains("early_stopping_patience"):
                early_stopping = EarlyStopping(
                    monitor=params.optimizer.monitor,
                    patience=params.optimizer.early_stopping_patience,
                    verbose=True,
                )
                callbacks.append(early_stopping)

            if params.optimizer.contains("lr_scheduler"):
                callback = mate.LearningRateMonitor(self.cache, "epoch")
                callbacks.append(callback)

        return (
            Trainer(
                max_epochs=params.max_epochs,
                gpus=(1 if params.cuda else None),
                callbacks=callbacks,
                logger=logger_module(params),
                enable_checkpointing=False,
            ),
            model,
            data_module,
        )

    def init(self):
        pass

    def create(self, path: str):
        pass

    def remove(self, model_name: str):
        action = "go"
        while action not in ("y", "n"):
            action = input(
                f'Are you sure you want to remove model "{model_name}"? (y/n)\n'
            )
        if action == "y":
            os.system(f"rm -r {os.path.join(self.root_folder, 'models', model_name)}")
            print(f"Removed model {model_name}")
        else:
            print("Ok, exiting.")

    def list(self, folder: str):
        print("\n".join(tuple("\t" + str(m) for m in self.__list_packages(folder))))

    def clone(self, source_model: str, target_model: str):
        os.system(
            f"cp -r {os.path.join(self.root_folder, 'models', source_model)} {os.path.join(self.root_folder, 'models', target_model)}"
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

        os.system(
            f"cp -r {os.path.join(self.root_folder, 'models', model_name)} {os.path.join(self.root_folder, 'snapshots', snapshot_name)}"
        )
        print(f"Created snapshot {snapshot_name}")

    def __fit(self, model_name: str, params: str):
        trainer, model, data_module = self.__get_trainer(model_name, params)
        trainer.fit(model, datamodule=data_module)

    def train(self, model_name: str, params: str = "default"):
        assert model_name in self.models, f'Model "{model_name}" does not exist.'
        print(f"Training model {model_name} with hyperparameters: {params}.json")

        self.__set_save_path(model_name, params)
        checkpoint_path = os.path.join(self.save_path, "model.pt")
        action = "go"
        if os.path.exists(checkpoint_path):
            while action not in ("y", "n", ""):
                action = input(
                    "Checkpiont file exists. Re-training will erase it. Continue? ([y]/n)\n"
                )
            if action in ("y", ""):
                os.remove(checkpoint_path)
            else:
                print("Ok, exiting.")
                return
        self.__fit(model_name, params)

    def test(self, model_name: str, params: str):
        assert model_name in self.models, f'Model "{model_name}" does not exist.'
        params = "parameters" if params == "" or params == "None" else params
        print(f"Testing model {model_name} with hyperparameters: {params}.json")

        trainer, model, data_module = self.__get_trainer(model_name, params)
        trainer.test(model, datamodule=data_module)

    def restart(self, model_name: str, params: str):
        assert model_name in self.models, f'Model "{model_name}" does not exist.'
        params = "parameters" if params == "" or params == "None" else params
        print(f"Restarting model {model_name} with parameters: {params}.json")

        self.is_restart = True
        self.__fit(model_name, params)

    def tune(self, model: str, params: tuple[str, ...]):
        pass

    def exec(self, model: str, file: str = ""):
        pass

    """ Import all submodules of a module, recursively, including subpackages
    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """

    def __import_submodules(self, package, recursive=True):

        if isinstance(package, str):
            package = importlib.import_module(package)
        results = {}
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
            full_name = package.__name__ + "." + name
            results[full_name] = importlib.import_module(full_name)
            if recursive and is_pkg:
                results.update(self.__import_submodules(full_name))
        return results
