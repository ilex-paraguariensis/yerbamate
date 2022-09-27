from bombilla import Bombilla
from yerbamate.package import Package
from .trainer import Trainer
from yerbamate.utils.bunch import Bunch
import tensorflow as tf
import ipdb


class KerasTrainer(Package):
    def __init__(
        self, params: Bunch, root_module, base_module, map_key_values, *kwargs
    ):

        super().__init__(params, *kwargs)

        self.bambilla = Bombilla(
            params,
            root_module=root_module,
            base_module=base_module,
            object_key_map=map_key_values,
        )
        self.install()

    def install(self):

        assert "trainer", "params must contain trainer"

        self.bambilla.load()
        self.bambilla.execute()

        self.bambilla.execute_method("compile", "trainer")

    def fit(self, *args, **kwargs):

        self.bambilla.execute_method("fit", "trainer", *args, **kwargs)

    def test(self, train_loader, val_loader):
        pass

    def save(self, path: str):
        pass

    def load(self, path: str):
        pass
