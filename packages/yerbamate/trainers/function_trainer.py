from yerbamate.parser.node import Node, NodeDict
from yerbamate.utils.bunch import Bunch
from .trainer import Trainer
import ipdb


class FunctionTrainer(Trainer):
    def __init__(
        self, params: Bunch, root_module, base_module, map_key_values, *kwargs
    ):
        super().__init__(params, *kwargs)

        # install objects from params
        #Node._root_module = root_module
        #Node._base_module = base_module
        #Node._key_value_map = map_key_values
        #self.install()
        self.root_node = NodeDict.create(root_module, base_module, map_key_values, params.clone())
        #Node._base_module = base_module
        #Node._root_module = root_module
        #Node._key_value_map = map_key_values


    def install(self):

        assert "train_function", "params must contain train_function"

        #root = self.params.clone()
        # ipdb.set_trace()

        #self.root_node = NodeDict(root)
        pass

    def fit(self, *args, **kwargs):
        self.root_node.__load__()

        self.root_node()

    def test(self, train_loader, val_loader):
        pass

    def save(self, path: str):
        pass

    def load(self, path: str):
        pass
