import torchmetrics


import torchmetrics
import torch as t


def denorm_image_to_tanh_quantize(x):
    bits = 8
    return ((x * 2 - 1) * (2**bits - 1)).int()


class DenormMSE(torchmetrics.MeanSquaredError):
    def __init__(self, denorm_fn=denorm_image_to_tanh_quantize, **kwargs):
        super().__init__(**kwargs)
        self.denorm_fn = denorm_fn

    def update(self, preds: t.Tensor, target: t.Tensor) -> None:
        return super().update(self.denrom_fn(preds), self.denorm_fn(target))


def denorm_tanh_to_image(x):
    return (x + 1) / 2


__all__ = ["DenormMSE", "denorm_tanh_to_image", "denorm_image_to_tanh_quantize"]