from pytorch_lightning import LightningModule
import torch as t
import torch.nn.functional as F
from argparse import Namespace
from .utils.visualize_predictions import visualize_predictions
from .utils.data_manager import DataManger


class BaseModel(LightningModule):
    def __init__(self, params: Namespace):
        super().__init__()
        self.params = params
        self.data_manager = DataManger(data_path=params.data_location)
        self.generator = t.nn.Sequential()

    def forward(self, z: t.Tensor) -> t.Tensor:
        return self.generator(z)

    def validation_step(self, batch: tuple[t.Tensor, t.Tensor], batch_idx: int):
        x, y = batch
        if batch_idx == 0:
            visualize_predictions(x, y, self(x), path=self.params.save_path)

        pred_y = self(x)
        loss = F.mse_loss(pred_y, y)
        self.log("val_mse", loss, prog_bar=True)
        return {"val_mse": loss}

    def test_step(self, batch: tuple[t.Tensor, t.Tensor], batch_idx: int):
        x, y = batch
        if batch_idx == 0:
            visualize_predictions(x, y, self(x), path=self.params.save_path)

        pred_y = self(x)
        se = F.mse_loss(pred_y, y, reduction="sum")
        denorm_pred_y = self.data_manager.denormalize(pred_y, self.device)
        denorm_y = self.data_manager.denormalize(y, self.device)
        ae = F.l1_loss(denorm_pred_y, denorm_y, reduction="sum")
        mask_pred_y = self.data_manager.discretize(denorm_pred_y, self.device)
        mask_y = self.data_manager.discretize(denorm_y, self.device)
        tn, fp, fn, tp = t.bincount(
            mask_y.flatten() * 2 + mask_pred_y.flatten(), minlength=4,
        )
        total_lengh = mask_y.numel()
        return {
            "se": se,
            "ae": ae,
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "tp": tp,
            "total_lengh": total_lengh,
        }

    def test_epoch_end(self, outputs):
        total_lenght = sum([x["total_lengh"] for x in outputs])
        mse = t.stack([x["se"] for x in outputs]).sum() / total_lenght
        mae = t.stack([x["ae"] for x in outputs]).sum() / total_lenght
        tn = t.stack([x["tn"] for x in outputs]).sum() / total_lenght
        fp = t.stack([x["fp"] for x in outputs]).sum() / total_lenght
        fn = t.stack([x["fn"] for x in outputs]).sum() / total_lenght
        tp = t.stack([x["tp"] for x in outputs]).sum() / total_lenght
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        accuracy = (tp + tn) / (tp + tn + fp + fn)
        f1 = 2 * precision * recall / (precision + recall)
        test_metrics = {
            "mse": mse,
            "mae": mae,
            "precision": precision,
            "recall": recall,
            "accuracy": accuracy,
            "f1": f1,
        }
        test_metrics = {k: v for k, v in test_metrics.items()}
        self.log("test_performance", test_metrics, prog_bar=True)
