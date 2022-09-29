from ..utils.bunch import Bunch
from ..package import Package


from typing import Optional, Union, Sequence, Type, Any


import ipdb


class Trainer(Package):
    def __init__(self, params, *kwargs):
        super().__init__(params, *kwargs)

    @staticmethod
    def create(params: Bunch, root_module, base_module, map_key_values, *kwargs):

        if "train_function" in params:
            from .function_trainer import FunctionTrainer

            return FunctionTrainer(
                params, root_module, base_module, map_key_values, *kwargs
            )

        if "pytorch_lightning_module" in params:
            from .lightning_trainer import (
                LightningTrainer,
            )  # importing it here avoids memory overload

            return LightningTrainer(params, root_module, base_module, map_key_values)
        else:
            from .keras_trainer import (
                KerasTrainer,
            )  # importing it here avoids memory overload

            return KerasTrainer(params, root_module, base_module, map_key_values)

    def generate_full_dict(self) -> tuple:

        assert hasattr(self, "bombilla"), "bombilla not found"
        full, err = self.bombilla.generate_full_dict()

        # remove empty or none values from error list
        err = [e for e in err if e is not None and len(e) > 0]
        return full, err

    def is_pl(self):
        return False

    def is_component(self, backbone: str, given_class: Type):
        return hasattr(given_class, "state_dict") and callable(given_class.state_dict)

    def fit(self) -> None:
        pass

    def test(self) -> None:
        pass

    def save(self, obj: Any, path: str) -> None:
        pass

    def load(self, obj: Any, path: str) -> None:
        pass


"""    
    def test(
        self,
        datamodule: Union[DataLoader, Sequence[DataLoader], LightningDataModule],
    ):
        self._trainer.test(model=self._module, datamodule=datamodule)

    def fit(self, datamodule: LightningDataModule):
        self._trainer.fit(
            model=self._module,
            train_dataloaders=datamodule.train_dataloader(),
            val_dataloaders=datamodule.val_dataloader(),
        )

    def save(
        self,
        obj: Union[t.nn.Module, t.optim.Optimizer, t.optim.lr_scheduler.StepLR],
        path: str,
    ):
        t.save(obj.state_dict(), path + ".pt")

    def load(
        self,
        obj: Union[t.nn.Module, t.optim.Optimizer, t.optim.lr_scheduler.StepLR],
        path: str,
    ):
        obj.load_state_dict(t.load(path))
"""

"""
keras package structure
├── dirname
│   ├── compile.py
│   ├── fit.py
│   ├── test.py
"""


def get_trainer_from_package(backbone: str, dirname: str) -> Trainer:
    if backbone == "keras":
        return KerasTrainer(dirname)
    elif backbone == "ligntning":
        return LightningTrainer(dirname)


def get_trainer_from_config(config: Bunch, *args, **kawrg) -> Trainer:
    if "pytorch_lightning_module" in config:
        return LightningTrainer(config, *args, **kawrg)
    elif "keras_model" in config:
        return KerasTrainer(config, *args, **kawrg)
    else:
        raise ValueError("No trainer specified in config")
    pass
