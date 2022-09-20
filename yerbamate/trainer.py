from yerbamate.bunch import Bunch
from yerbamate import parser
from .package import Package


from abc import ABC, abstractmethod
from pickle import LONG_BINGET
from typing import Optional, Union, Sequence, Type, Any
import os

import torch as t
from torch.utils.data import DataLoader
from pytorch_lightning import (
    Trainer as LightningTrainer,
    LightningModule,
    LightningDataModule,
)
import tensorflow as tf
from .package import Package


class Trainer(Package):
    _lightning_module: LightningModule
    _lightning_trainer: LightningTrainer
    _keras_model: tf.keras.Model

    def __init__(self, data_module, **params):
        self.data_module = data_module
        super().__init__(**params)

    def is_pl():
        return False

    def is_component(self, backbone: str, given_class: Type):
        return hasattr(given_class, "state_dict") and callable(given_class.state_dict)

    def fit(self) -> None:
        if self.backbone == "lightning":
            self._lightning_trainer.fit(
                self._lightning_module,
                self.data_module.train_loader(),
                self.data_module.val_loader(),
            )
        elif self.backbone == "keras":
            self._keras_model.fit(
                self.data_module.train_loader(), self.data_module.val_loader()
            )

    def test(self) -> None:
        if self.backbone == "lightning":
            self._lightning_trainer.test(
                self._lightning_module, self.data_module.test_loader()
            )
        elif self.backbone == "keras":
            self._keras_model.test(self.data_module.test_loader())

    def save(self, obj: Any, path: str) -> None:
        pass

    def load(self, obj: Any, path: str) -> None:
        pass


"""    
    def test(
        self,
        datamodule: Union[DataLoader, Sequence[DataLoader], LightningDataModule],
    ):
        self._trainer.test(model=self._module, datamodule=datamodule)

    def fit(self, datamodule: LightningDataModule):
        self._trainer.fit(
            model=self._module,
            train_dataloaders=datamodule.train_dataloader(),
            val_dataloaders=datamodule.val_dataloader(),
        )

    def save(
        self,
        obj: Union[t.nn.Module, t.optim.Optimizer, t.optim.lr_scheduler.StepLR],
        path: str,
    ):
        t.save(obj.state_dict(), path + ".pt")

    def load(
        self,
        obj: Union[t.nn.Module, t.optim.Optimizer, t.optim.lr_scheduler.StepLR],
        path: str,
    ):
        obj.load_state_dict(t.load(path))
"""

"""
keras package structure
├── dirname
│   ├── compile.py
│   ├── fit.py
│   ├── test.py
"""


class KerasTrainer(Trainer):
    @staticmethod
    def is_component(given_class: Type):
        return hasattr(given_class, "state_dict") and callable(given_class.state_dict)

    model: tf.keras.Model

    def _generate(self, filename: str) -> dict:
        pass

    def _parse(self, args: dict) -> tuple[tf.keras.Model, callable]:

        components = tuple(
            (key, val) for (key, val) in args.items() if val.get("is_component")
        )

        assert (
            len(components) == 1
        ), "Only one component can be specified in the run config"

    def __init__(self, dirname: str, run_config: dict):
        compile_config = self._generate(os.path.join(dirname, "config.py"))
        fit_config = self._generate(os.path.join(dirname, "fit.py"))
        test_config = self._generate(os.path.join(dirname, "test.py"))
        self.args = {
            "compile": compile_config,
            "fit": fit_config,
            "test": test_config,
        }
        # TODO: assert that the given run_config has the same keys as the args, recursively
        self._parse(run_config)()
        self.fit = self._parse(run_config)
        self.test = self._parse(run_config)
        self.model = self._parse(run_config)

    def fit(self, train_loader, val_loader):
        pass

    def test(self, train_loader, val_loader):
        pass

    def save(self, path: str):
        pass

    def load(self, path: str):
        pass


class LightningTrainer(Package):
    def __init__(
        self, params: Bunch, root_module, base_module, map_key_values, *kwargs
    ):
        super().__init__(params, *kwargs)

        self.install(root_module, base_module, map_key_values)

    def install(self, root_module: str, base_module: str, map_key_values: dict):

        assert (
            "pytorch_lightning_module" and "trainer" and "data" in self.params
        ), "params must contain pytorch_lightning_module, trainer and data"

        # install objects from params
        # ipdb.set_trace()
        objects = parser.load_python_object(
            self.params, self.params.clone(), root_module, base_module, map_key_values
        )

        self.objects = objects
        self.trainer = objects["trainer"]
        self.model = objects["pytorch_lightning_module"]
        self.datamodule = objects["data"]

        # rename

    def is_pl(self):
        return True

    def fit(self, *args, **kwargs):
        self.trainer.fit(self.model, datamodule=self.datamodule, *args, **kwargs)

    def test(self, *args, **kwargs):
        self.trainer.test(self.model, datamodule=self.datamodule, *args, **kwargs)
        pass

    def save(self, path: str):
        pass

    def load(self, path: str):
        pass


def get_trainer_from_package(backbone: str, dirname: str) -> Trainer:
    if backbone == "keras":
        return KerasTrainer(dirname)
    elif backbone == "ligntning":
        return LightningTrainer(dirname)


def get_trainer_from_config(config: Bunch, *args, **kawrg) -> Trainer:
    if "pytorch_lightning_module" in config:
        return LightningTrainer(config, *args, **kawrg)
    elif "keras_model" in config:
        return KerasTrainer(config, *args, **kawrg)
    else:
        raise ValueError("No trainer specified in config")
    pass
