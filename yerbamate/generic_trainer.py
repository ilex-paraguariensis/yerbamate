from .parse import Parser
from .package import Package
from yerbamate import parser
from .bunch import Bunch
from .trainer import Trainer
import ipdb


class GenericTrainer(Trainer):
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
            "trainer" and "data" in self.params
        ), "params must contain trainer and data"

        root = self.params.clone()
        objects = self.parser.load_python_object(root)

        self.objects = objects

    def fit(self, *args, **kwargs):

        self.parser.call_method(self.params.trainer, "fit", *args, **kwargs)

    def test(self, *args, **kwargs):

        self.parser.call_method(self.params.trainer, "test", *args, **kwargs)

    def save(self, path: str):
        pass

    def load(self, path: str):
        pass
