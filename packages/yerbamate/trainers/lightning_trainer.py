from ..bombilla.node import Node, NodeDict
from ..bombilla.parse import Parser
from ..package import Package
from ..utils.bunch import Bunch
from .trainer import Trainer
import ipdb


class LightningTrainer(Trainer):
    def __init__(
        self, params: Bunch, root_module, base_module, map_key_values, *kwargs
    ):
        super().__init__(params, *kwargs)

        Node._root_module = root_module
        Node._base_module = base_module
        Node._key_value_map = map_key_values
        # self.parser = Parser(
        #     root_module=root_module,
        #     base_module=base_module,
        #     map_key_values=map_key_values,
        # )
        self.install()

    def install(self):

        assert (
            "pytorch_lightning_module" and "trainer" and "data" in self.params
        ), "params must contain pytorch_lightning_module, trainer and data"

        # install objects from params
        # ipdb.set_trace()
        root = self.params.clone()
        
        self.root_node = NodeDict(root)
        ipdb.set_trace()
        # ipdb.set_trace()
        self.root_node.__load__()

        objects = self.root_node()


        self.objects = objects
        # self.trainer = objects["trainer"]
        # self.model = objects["pytorch_lightning_module"]
        # self.datamodule = objects["data"]

        # rename

    def is_pl(self):
        return True

    def fit(self, *args, **kwargs):
        # ipdb.set_trace()
        # ipdb.set_trace()
        self.root_node.trainer_node.call_method("fit", *args, **kwargs)
        # self.trainer.fit(self.model, datamodule=self.datamodule, *args, **kwargs)

    def test(self, *args, **kwargs):
        # self.trainer.test(self.model, datamodule=self.datamodule, *args, **kwargs)
        self.root_node.trainer_node.call_method("test", *args, **kwargs)

    def save(self, path: str):
        pass

    def load(self, path: str):
        pass
