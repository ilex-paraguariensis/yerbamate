#!env python
from argparse import ArgumentParser, Namespace
import os
import torch as t
import json
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import EarlyStopping
from .plot import plot
from .tune_hyperparameters import tune

# FIXME: cannot run snapshost due to name


def run():
    print('hello from mate!!')
    current_dir = os.path.dirname(os.path.realpath(__file__))
    # with open(os.path.join("dlm", "default_parameters.json")) as f:
    #    default_params = json.load(f)

    parser = ArgumentParser()
    cur_folder = os.path.dirname(__file__)

    parser.add_argument(
        "action",
        help="train or test the model",
        choices=(
            "init",
            "train",
            "test",
            "list",
            "remove",
            "snapshot-create",
            "snapshot-run",
            "snapshot-list",
            "snapshot-remove",
            "tune",
            "create",
            "restart",
            "clone",
            "merge-results",
            "exec",
        ),
    )
    parser.add_argument(
        "model",
        default="",
        type=str,
        nargs="?",
        help="Model to use. Must exist in dl/models/",
    )
    parser.add_argument(
        "target",
        help="target name to use. Used by 'clone' and 'snapshot'",
        nargs="?",
        default=os.path.join(current_dir, "results"),
    )
    """
    for key, value in default_params.items():
        parser.add_argument(
            "--" + key, help=key + " to use", default=value, type=type(value),
        )
    """

    args = parser.parse_args()
    models_choices = (
        tuple(
            x
            for x in os.listdir(os.path.join("dl", "models"))
            if not "__" in x
        )
        if os.path.exists(os.path.join("dl", "models"))
        else tuple()
    )

    # assert "__" not in params.model, "Models cannot have '__' in their name"

    cur_folder = os.path.basename(os.path.dirname(__file__))

    if args.action == "init":
        os.system(f"cp -r {os.path.join(cur_folder, 'dl')} .")

    elif args.action == "create":
        os.mkdir(f"{os.path.join('dl', 'models', args.model)}")
        target_dir = os.path.join("dl", "models", args.model)
        os.system(
            f"cp -r {os.path.join(cur_folder, 'dl', 'example')}* {os.path.join('dl', 'models', args.model)}"
        )
        print(f"Created model {args.model} at {target_dir}")

    elif args.action == "remove":
        action = "go"
        while action not in ("y", "n"):
            action = input(
                f'Are you sure you want to remove model "{args.model}"? (y/n)\n'
            )
        if action == "y":
            os.system(f"rm -r {os.path.join('dl', 'models', args.model)}")
            print(f"Removed model {args.model}")
        else:
            print("Ok, exiting.")

    elif args.action == "clone":
        os.system(
            f"cp -r {os.path.join('dl', 'models', args.model)} {os.path.join('dl', 'models', args.target)}"
        )

    elif args.action == "list":
        print("\n".join(f"\t{u}" for u in models_choices))

    elif args.action == "snapshot-create":
        snapshot_names = [
            name.split("__")
            for name in os.listdir(os.path.join("dl", "snapshots"))
        ]
        matching_snapshots = [
            name for name in snapshot_names if name[0] == args.model
        ]
        max_version_matching = (
            max([int(name[1]) for name in matching_snapshots])
            if len(matching_snapshots) > 0
            else 0
        )
        snapshot_name = f"{args.model}__{max_version_matching + 1}"
        os.system(
            f"cp -r {os.path.join('dl', 'models', args.model)} {os.path.join('dl', 'snapshots', snapshot_name)}"
        )
        print(f"Created snapshot {snapshot_name}")

    elif args.action == "snapshot-list":
        print(os.listdir(os.path.join("dl", "snapshots")))

    else:
        assert (
            args.model in models_choices
        ), f"Model {args.model} does not exist."
        with open(
            os.path.join("dl", "models", args.model, "default_parameters.json")
        ) as f:
            params = Namespace()
            params.__dict__ = json.load(f)

        # for key, val in model_specific_params.items():
        #    # if key not in params.__dict__:
        #    args.__dict__[key] = val

        print(json.dumps(params.__dict__, indent=4))
        model_module = __import__(
            f"dl.{'models' if args.action != 'snapshot-run' else 'snapshots'}.{args.model}.model",
            fromlist=["models"],
        )
        data_loader_module = __import__(
            f"dl.data_loader", fromlist=["data_loader"]
        )
        logger_module = __import__(f"{cur_folder}.logger", fromlist=["logger"])
        save_path = os.path.join("dl", "models", args.model)
        params.save_path = save_path

        if args.action in ("train", "test", "restart", "exec"):
            model = model_module.Model(params)
            print(model)
            if not args.action == "exec":
                data_module = data_loader_module.CustomDataModule(params)
                trainer = Trainer(
                    max_epochs=params.max_epochs,
                    gpus=(1 if params.cuda else None),
                    callbacks=[
                        EarlyStopping(
                            monitor="val_loss",
                            patience=params.early_stopping_patience,
                        ),
                        # checkpoint_callback,
                    ],
                    logger=logger_module.CustomLogger(params),
                    enable_checkpointing=False,
                )

        checkpoint_path = os.path.join(save_path, "checkpoint.ckpt")
        if args.action == "train" and os.path.exists(checkpoint_path):
            action = "go"
            while action not in ("y", "n", ""):
                action = input(
                    "Checkpiont file exists. Re-training will erase it. Continue? ([y]/n)\n"
                )
            if action in ("y", ""):
                os.remove(checkpoint_path)
            else:
                print("Ok, exiting.")
                return

        if args.action in ("restart", "test", "exec"):
            if os.path.exists(checkpoint_path):
                print(f"\nLoading model from checkpoint:'{checkpoint_path}'\n")
                model.load_state_dict(t.load(checkpoint_path))
            else:
                raise Exception(
                    "No checkpoint found. You must train the model first!"
                )
        if args.action == "tune":
            tune(
                params, model_module.Model, data_loader_module.CustomDataModule
            )

        if args.action in ("train", "restart"):
            trainer.fit(model=model, datamodule=data_module)
            print(f"Saving model to {checkpoint_path}")
            t.save(model.cpu().state_dict(), checkpoint_path)
        if args.action in ("test", "train", "restart"):
            trainer.test(model=model, datamodule=data_module)
            plot(save_path)
        elif args.action == "exec":
            assert (
                "exec" in params.__dict__
            ), 'No "exec" file defined in parameters.json file.'
            custom_exec = __import__(
                f"dl.{params.exec}", fromlist=["custom_test"],
            ).main
            custom_exec(model)


if __name__ == "__main__":
    run()
