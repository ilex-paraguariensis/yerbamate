from ...base_model import BaseModel
from ...models_components.resnet3d import ResNet3DAutoEncoder
from argparse import ArgumentParser
import torch.nn.functional as F
import torch as t


class Model(BaseModel):
    def __init__(self, params):
        super().__init__(params)
        self.generator = ResNet3DAutoEncoder(params)

    def loss(self, x, y):
        return F.mse_loss(x, y)

    def training_step(self, batch: tuple[t.Tensor, t.Tensor], batch_idx: int):
        x, y = batch
        y_pred = self(x)
        loss = self.loss(y_pred, y)
        return loss

    def configure_optimizers(self):
        return t.optim.Adam(self.parameters(), lr=self.params.lr)
