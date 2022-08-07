from pytorch_lightning.loggers import LightningLoggerBase, TensorBoardLogger
import torch as t
import json
import csv
import os
import ipdb
from argparse import Namespace


class CustomLogger(TensorBoardLogger):
    def __init__(self, params: Namespace):
        super().__init__("logs", params.model_name)
        # ipdb.set_trace()
        self.params = params
        # self.log("val_loss", 0.1)


class CustomLoggerz(LightningLoggerBase):
    def __init__(
        self,
        params: Namespace,
        train_header: tuple[str, ...] = ("epoch", "train_mse", "val_mse"),
    ):
        super().__init__()
        self.params = params
        self.csv_path = os.path.join(params.save_path, "training_log.csv")
        self.last_train_mse_loss = -1.0
        with open(self.csv_path, "w") as f:
            writer = csv.writer(f)
            writer.writerow(train_header)

    def write_performance_csv(self, name, metrics):
        if name == "test":
            metrics["epoch"] = 1
        performance_name = f"{name}_performance"
        file_path = os.path.join(self.params.save_path, f"{performance_name}.csv")
        if metrics["epoch"] > 0:
            if metrics["epoch"] == 1:
                if os.path.exists(file_path):
                    os.remove(file_path)
                with open(file_path, "w") as f:
                    writer = csv.writer(f)
                    writer.writerow(metrics[performance_name].keys())

            with open(file_path, "a") as f:
                writer = csv.writer(f)
                writer.writerow(
                    tuple(val for _, val in metrics[performance_name].items())
                )

    def log_metrics(self, metrics, step: int):
        for condition in ["train", "val", "test"]:
            if f"{condition}_performance" in metrics:
                self.write_performance_csv(condition, metrics)

    @property
    def name(self):
        return "CustomLogger"

    def log_hyperparams(self, hparams):
        pass

    @property
    def version(self):
        pass
