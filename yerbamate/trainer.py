from .package import Package


from abc import ABC, abstractmethod
from pickle import LONG_BINGET
from typing import Optional, Union, Sequence, Type, Any
import os

import torch as t
from torch.utils.data import DataLoader
from pytorch_lightning import (
    Trainer as LightningBuiltinTrainer,
    LightningModule,
    LightningDataModule,
)
import tensorflow as tf
from .package import Package


class Trainer(Package):
    @staticmethod
    def is_component(given_class: Type):
        return hasattr(given_class, "state_dict") and callable(
            given_class.state_dict
        )

    def __init__(self, dirname: str):
        self.dirname = dirname

    @abstractmethod
    def fit(self, train_loader, val_loader) -> None:
        pass

    @abstractmethod
    def test(self, datamodule) -> None:
        pass

    @abstractmethod
    def save(self, obj: Any, path: str) -> None:
        pass

    @abstractmethod
    def load(self, obj: Any, path: str) -> None:
        pass

    @abstractmethod
    def models(self) -> list:
        pass


class LightningTrainer(Trainer):
    @staticmethod
    def is_component(given_class: Type):
        return hasattr(given_class, "state_dict") and callable(
            given_class.state_dict
        )

    _module: LightningModule
    _trainer: LightningBuiltinTrainer

    def __init__(self, folder: str):
        super().__init__(folder)

    def test(
        self,
        datamodule: Union[
            DataLoader, Sequence[DataLoader], LightningDataModule
        ],
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
        obj: Union[
            t.nn.Module, t.optim.Optimizer, t.optim.lr_scheduler.StepLR
        ],
        path: str,
    ):
        t.save(obj.state_dict(), path + ".pt")

    def load(
        self,
        obj: Union[
            t.nn.Module, t.optim.Optimizer, t.optim.lr_scheduler.StepLR
        ],
        path: str,
    ):
        obj.load_state_dict(t.load(path))


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
        return hasattr(given_class, "state_dict") and callable(
            given_class.state_dict
        )

    model: tf.keras.Model

    def _generate(self, filename: str) -> dict:
        pass

    def _parse(self, args: dict) -> tuple[tf.keras.Model, callable]:

        components = tuple(
            (key, val)
            for (key, val) in args.items()
            if val.get("is_component")
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


def get_trainer_from_package(backbone: str, dirname: str) -> Trainer:
    if backbone == "keras":
        return KerasTrainer(dirname)
    elif backbone == "ligntning":
        return LightningTrainer(dirname)
