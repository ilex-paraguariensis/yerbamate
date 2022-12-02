from bombilla import Bombilla

from ..utils.bunch import Bunch
from .trainer import Trainer
import ipdb


class LightningTrainer(Trainer):
    def __init__(self, params: Bunch, root_module, map_key_values, *kwargs):
        super().__init__(params, *kwargs)

        self.bombilla = Bombilla(
            params,
            root_module=root_module,
            object_key_map=map_key_values,
        )
        self.install()

    def install(self):
        assert (
            "pytorch_lightning_module" and "trainer" and "data" in self.params
        ), "params must contain pytorch_lightning_module, trainer and data"

        self.bombilla.load()

    def is_pl(self):
        return True

    def fit(self, *args, **kwargs):
        # ipdb.set_trace()
        self.bombilla.execute()

        if self.bombilla.has_method("fit", "trainer"):
            self.bombilla.execute_method("fit", "trainer", *args, **kwargs)

        else:
            self.bombilla["trainer"].fit(
                self.bombilla["pytorch_lightning_module"],
                self.bombilla["data"],
                *args,
                **kwargs
            )

    def test(self, *args, **kwargs):

        if self.bombilla.has_method("test", "trainer"):
            self.bombilla.execute_method("fit", "trainer", *args, **kwargs)

        else:
            self.bombilla["trainer"].test(
                self.bombilla["pytorch_lightning_module"],
                self.bombilla["data"],
                *args,
                **kwargs
            )

    def save(self, path: str):
        pass

    def load(self, path: str):
        pass
