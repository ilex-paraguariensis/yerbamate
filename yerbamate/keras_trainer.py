from .node import Node, NodeDict
from .package import Package
from .trainer import Trainer
from . import parser
from .bunch import Bunch
import tensorflow as tf
import ipdb


class KerasTrainer(Package):
    def __init__(
        self, params: Bunch, root_module, base_module, map_key_values, *kwargs
    ):

        super().__init__(params, *kwargs)

        # install objects from params
        Node._root_module = root_module
        Node._base_module = base_module
        Node._key_value_map = map_key_values
        self.install()

    def install(self):

        assert "trainer", "params must contain trainer"

        root = self.params.clone()
        # ipdb.set_trace()

        self.root_node = NodeDict(root)
        self.root_node = self.root_node.__load__()

        objects = self.root_node()

        # ipdb.set_trace()
        self.root_node.trainer_node.call_method("compile")

        self.objects = objects

    def fit(self, *args, **kwargs):
        # ipdb.set_trace()
        self.root_node.trainer_node.call_method("fit", *args, **kwargs)

    def test(self, train_loader, val_loader):
        pass

    def save(self, path: str):
        pass

    def load(self, path: str):
        pass
