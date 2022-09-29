from bombilla import Bombilla

from ..utils.bunch import Bunch
from .trainer import Trainer
import ipdb


class LightningTrainer(Trainer):
    def __init__(
        self, params: Bunch, root_module, base_module, map_key_values, *kwargs
    ):
        super().__init__(params, *kwargs)

        self.bombilla = Bombilla(
            params,
            root_module=root_module,
            base_module=base_module,
            object_key_map=map_key_values,
        )
        self.install()

    def install(self):
        assert (
            "pytorch_lightning_module" and "trainer" and "data" in self.params
        ), "params must contain pytorch_lightning_module, trainer and data"

        self.bombilla.load()
        self.bombilla.execute()

        # rename

    def is_pl(self):
        return True

    def fit(self, *args, **kwargs):
        # ipdb.set_trace()

        # ipdb.set_trace()

        self.bombilla.execute_method("fit", "trainer", *args, **kwargs)
        # self.root_node.trainer_node.call_method("fit", *args, **kwargs)
        # self.trainer.fit(self.model, datamodule=self.datamodule, *args, **kwargs)

    def test(self, *args, **kwargs):
        # self.trainer.test(self.model, datamodule=self.datamodule, *args, **kwargs)
        self.bombilla.execute_method("fit", "trainer", *args, **kwargs)

        # self.root_node.trainer_node.call_method("test", *args, **kwargs)

    def save(self, path: str):
        pass

    def load(self, path: str):
        pass
