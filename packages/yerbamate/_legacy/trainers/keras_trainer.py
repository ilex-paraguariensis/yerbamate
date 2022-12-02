from bombilla import Bombilla
from .trainer import Trainer
from yerbamate.utils.bunch import Bunch
import ipdb


class KerasTrainer(Trainer):
    def __init__(self, params: Bunch, root_module, map_key_values, *kwargs):

        super().__init__(params, *kwargs)

        self.bombilla = Bombilla(
            params,
            root_module=root_module,
            object_key_map=map_key_values,
        )
        self.install()

    def install(self):

        assert "trainer", "params must contain trainer"

        self.bombilla.load()

    def fit(self, *args, **kwargs):

        self.bombilla.execute()

        if self.bombilla.has_method("compile", "trainer"):
            self.bombilla.execute_method("compile", "trainer")

        if self.bombilla.has_method("fit", "trainer"):
            self.bombilla.execute_method("fit", "trainer", *args, **kwargs)
        else:
            self.bombilla.call_all_methods("trainer")

    def test(self, train_loader, val_loader):
        pass

    def save(self, path: str):
        pass

    def load(self, path: str):
        pass
