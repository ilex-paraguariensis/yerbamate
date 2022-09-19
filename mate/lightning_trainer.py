from .trainer import Trainer
from pytorch_lightning import LightningModule, LightningDataModule, Trainer as LightningBuiltinTrainer


class LightningTrainer(Trainer):
    _lightning_module: LightningModule
    _lightning_trainer: LightningBuiltinTrainer

    def __init__(self, pytorch_lightning_trainer:LightningBuiltinTrainer, pytorch_lightning_module:LightningModule):
        self.trainer = pl_trainer 
        self.module = pytorch_lightning_module 

    def fit(self, datamodule) -> None:
        self.trainer.fit(self.module, datamodule)

    def test(self, datamodule) -> None:
        self.trainer.test(self.module, datamodule)



