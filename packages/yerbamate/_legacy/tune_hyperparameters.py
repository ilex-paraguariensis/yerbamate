import pytorch_lightning as pl
import os
from argparse import Namespace
import argparse
import os
from typing import Optional
import optuna
from optuna.integration import PyTorchLightningPruningCallback
from packaging import version
import pytorch_lightning as pl
import torch
from copy import deepcopy
from optuna.visualization import plot_optimization_history


def tune(params: Namespace, model_class, data_loader_class):
    params.max_epochs = 1

    def objective(trial: optuna.trial.Trial) -> float:

        # We optimize the number of layers, hidden units in each layer and dropouts.
        train_batch_size = trial.suggest_int("train_batch_size", 2, 32)
        kernel_size = trial.suggest_int("kernel_size", 3, 7)
        local_params = deepcopy(params)
        local_params.train_batch_size = train_batch_size
        local_params.kernel_size = kernel_size
        model = model_class(local_params)
        datamodule = data_loader_class(local_params)

        trainer = pl.Trainer(
            logger=True,
            enable_checkpointing=False,
            max_epochs=params.max_epochs,
            gpus=1 if torch.cuda.is_available() else None,
            callbacks=[PyTorchLightningPruningCallback(trial, monitor="val_acc")],
        )
        values = dict(train_batch_size=train_batch_size)
        hyperparameters = Namespace()
        hyperparameters.__dict__ = values
        trainer.logger.log_hyperparams(hyperparameters)
        trainer.fit(model, datamodule=datamodule)

        return trainer.callback_metrics["val_acc"].item()

    args = Namespace()
    args.pruning = True
    pruner: optuna.pruners.BasePruner = (
        optuna.pruners.MedianPruner() if args.pruning else optuna.pruners.NopPruner()
    )
    study = optuna.create_study(direction="maximize", pruner=pruner)
    study.optimize(objective, n_trials=100, timeout=600)

    print(f"Number of finished trials: {len(study.trials)}")

    print("Best trial:")
    trial = study.best_trial

    print("  Value: {}".format(trial.value))

    print("  Params: ")
    for key, value in trial.params.items():
        print("    {}: {}".format(key, value))

    plot_optimization_history(study)
    return objective
