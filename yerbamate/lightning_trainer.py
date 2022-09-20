from .parse import Parser
from .package import Package
from yerbamate import parser
from .bunch import Bunch
from .trainer import Trainer
import ipdb


class LightningTrainer(Trainer):
    def __init__(
        self, params: Bunch, root_module, base_module, map_key_values, *kwargs
    ):
        super().__init__(params, *kwargs)

        self.parser = Parser(
            root_module=root_module,
            base_module=base_module,
            map_key_values=map_key_values,
        )
        self.install()

    def install(self):

        assert (
            "pytorch_lightning_module" and "trainer" and "data" in self.params
        ), "params must contain pytorch_lightning_module, trainer and data"

        # install objects from params
        # ipdb.set_trace()
        root = self.params.clone()
        objects = self.parser.load_python_object(root)

        # ipdb.set_trace()

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

    def save(self, path: str):
        pass

    def load(self, path: str):
        pass
