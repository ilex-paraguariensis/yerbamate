from .package import Package
from yerbamate import parser
from .bunch import Bunch
from .trainer import Trainer

    
class LightningTrainer(Trainer):
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

    def save(self, path: str):
        pass

    def load(self, path: str):
        pass



