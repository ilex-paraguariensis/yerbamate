from bombilla import Bombilla
from yerbamate.utils.bunch import Bunch
from .trainer import Trainer
import ipdb


class FunctionTrainer(Trainer):
    def __init__(self, params: Bunch, root_module, map_key_values, *kwargs):
        super().__init__(params, *kwargs)

        # install objects from params
        self.bombilla = Bombilla(
            params,
            root_module=root_module,
            object_key_map=map_key_values,
        )
        self.install()

    def install(self):

        assert "train_function", "params must contain train_function"
        self.bombilla.load()

        # root = self.params.clone()
        # # ipdb.set_trace()

        # self.root_node = NodeDict(root)

    def fit(self, *args, **kwargs):

        self.bombilla.execute()

    def test(self, train_loader, val_loader):
        pass

    def save(self, path: str):
        pass

    def load(self, path: str):
        pass
