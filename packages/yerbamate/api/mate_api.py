import json
import os
import queue
import sys
import threading
from time import sleep
from yerbamate.mate_config import MateConfig
from yerbamate.mateboard.mateboard import MateBoard
from yerbamate.trainers.trainer import Trainer
from yerbamate.utils.bunch import Bunch

from .data.package_repository import PackageRepository

from typing import Optional, Union
import ipdb


import asyncio
import websocket
import websockets
from .socket import WebSocketServer

"""
MATE API

"""

from multiprocessing import Process, Queue


class MateAPI:
    def __init__(self, config: MateConfig):
        self.config: MateConfig = config
        self.repository = PackageRepository(config)
        self.exp: Optional[Bunch] = None
        self.exp_name: Optional[str] = None
        self.save_dir: Optional[str] = None
        self.checkpoint_path: Optional[str] = None
        self.trainer: Optional[Trainer] = None

    def list(self, module: str, query: Optional[str] = None):
        return self.repository.list(module, query)

    def load_experiment(self, experiment_name: str):
        return self.repository.local.load_experiment(experiment_name)

    def select_experiment(self, experiment_name: str):

        self.repository.local.assert_experiment_exists(experiment_name)
        self.exp, self.save_dir = self.repository.local.load_experiment(experiment_name)
        self.exp_name = experiment_name

    def init_trainer(self):

        assert self.exp and self.save_dir, "You must select an experiment first"

        # TODO, .env file

        map_key_value = {
            "save_path": self.save_dir,
            "save_dir": self.save_dir,
        }
        root_module = f"{self.config.project}"

        self.trainer = Trainer.create(self.exp, root_module, map_key_value)

    def validate_params(self):
        assert (
            self.trainer is not None
        ), "Trainer must be initialized before parsing params (Bombilla is managed by Trainer)"

        full, err = self.trainer.generate_full_dict()

        if len(err) > 0:
            print(f"Errors in {self.exp_name}")
            for error in err:
                print(error)

            sys.exit(1)

        # io.save_train_experiments(self.save_path, full, self.config)

        return full

    def train(self):
        # ensure that this runs on the main loop
        print("train")
        self.init_trainer()
        self.validate_params()
        assert self.trainer is not None
        self.trainer.fit()

    def restart(self):
        # TODO, this should be in the trainer
        pass

    def test(self):
        # TODO, this should be in the trainer
        pass

    def sample(self):
        # TODO, this should be in the trainer if its a generative model
        pass

        """
    These probably should be in the trainer
    """

    def set_checkpoint_path(self):
        assert self.exp and self.save_dir, "You must select an experiment first"
        checkpoint_path = os.path.join(self.save_dir, "checkpoints")
        if not os.path.exists(checkpoint_path):
            os.makedirs(checkpoint_path)
        self.checkpoint_path = checkpoint_path

    def delete_checkpoints(self):
        assert self.checkpoint_path is not None
        checkpoints = [
            os.path.join(self.checkpoint_path, p)
            for p in os.listdir(self.checkpoint_path)
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

    """
    def query_models(self, query: Optional[str] = None):
        return self.remote.get_models(query)

    def query_trainers(self, query: str = None):
        return self.remote.get_trainers(query)

    def query_datasets(self, query: str = None):
        return self.remote.get_data_loaders(query)

    def install_model(self, model: Package):
        self.local.add_model(model)
    """
