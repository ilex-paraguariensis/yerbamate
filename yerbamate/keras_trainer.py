from .package import Package
from .trainer import Trainer
import tensorflow as tf


class KerasTrainer(Package):
    def __init__(self, dirname: str, run_config: dict):
        compile_config = self._generate(os.path.join(dirname, "config.py"))
        fit_config = self._generate(os.path.join(dirname, "fit.py"))
        test_config = self._generate(os.path.join(dirname, "test.py"))
        self.args = {
            "compile": compile_config,
            "fit": fit_config,
            "test": test_config,
        }
        # TODO: assert that the given run_config has the same keys as the args, recursively
        self._parse(run_config)()
        self.fit = self._parse(run_config)
        self.test = self._parse(run_config)
        self.model = self._parse(run_config)

    @staticmethod
    def is_component(given_class: Type):
        return hasattr(given_class, "state_dict") and callable(given_class.state_dict)

    model: tf.keras.Model

    def _generate(self, filename: str) -> dict:
        pass

    def _parse(self, args: dict) -> tuple[tf.keras.Model, callable]:

        components = tuple(
            (key, val) for (key, val) in args.items() if val.get("is_component")
        )

        assert (
            len(components) == 1
        ), "Only one component can be specified in the run config"

    
    def fit(self, train_loader, val_loader):
        pass

    def test(self, train_loader, val_loader):
        pass

    def save(self, path: str):
        pass

    def load(self, path: str):
        pass


