from .package import Package
from .trainer import Trainer
from . import parser
from .bunch import Bunch
import tensorflow as tf
import ipdb
import os

class KerasTrainer(Package):
    def __init__(self, params: Bunch, root_module, base_module, map_key_values, *kwargs):

        super().__init__(params, *kwargs)
        assert (
            "keras_training_module" and "data" in self.params
        ), "params must contain keras_training_module, trainer and data"

        # install objects from params
        objects = parser.load_python_object(
            self.params, self.params.clone(), root_module, base_module, map_key_values
        )
        self.objects = objects
        # self.trainer = objects["trainer"]
        self.training_module = objects["keras_training_module"]
        self.training_module.compile()
        self.datamodule = objects["data"]

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

    
    def fit(self):
        self.training_module.fit(self.datamodule.train_dataloader(), self.datamodule.val_dataloader())

    def test(self, train_loader, val_loader):
        pass

    def save(self, path: str):
        pass

    def load(self, path: str):
        pass


