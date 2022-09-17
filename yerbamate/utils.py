import inspect
from typing import Callable
import ipdb
import os
from itertools import chain
import json

from .bunch import Bunch

default_dict = {str: "", int: 0, float: 0.0}


def get_function_parameters(function: Callable):
    parameters = {
        val.name: (
            val.default
            if val.default != inspect._empty
            else default_dict.get(val.annotation, None)
        )
        for _, val in inspect.signature(function).parameters.items()
        if val.name != "self"
    }
    return parameters


def migrate_mate_version(config: Bunch, root_project: str):

    from . import __version__
    import yerbamate.migrator as migrator

    if config.mate_version == __version__:  # pragma: no cover
        return config

    # handle migration from current_version to __version__
    migrator = migrator.Migration(root_project, config.mate_version, __version__)

    success = migrator.migrate()
    if not success:
        raise Exception(
            "Migration failed, please send the logs and open an issue on github"
        )

    config.mate_version = __version__

    with open(os.path.join(root_project, "mate.json"), "w") as f:
        json.dump(config, f, indent=4)

    print("Migration sucessfull!")
    return Bunch(config)

    # if self.config.mate_version != __version__:
    #     print(
    #         f"New mate version has been installed. Going to handle migration from {self.config.mate_version} to {__version__}"
    #     )
    #     migrator = Migration(
    #         self.root_folder, self.config.mate_version, __version__
    #     )
    #     success = migrator.migrate()
    #     if not success:
    #         print(
    #             "Migration failed... please check the logs and make an issue on github"
    #         )
    #         # sys.exit(1)
    #     else:
    #         self.config.mate_version = __version__
    #         with open(path, "w") as f:
    #             json.dump(self.config, f, indent=4)
    #         print("Migration successful")

    pass


def get_model_parameters(path: str):
    path = path.replace("/", ".")
    model_class = __import__(
        f"{path}.model",
        fromlist=[path.split(".")[1]],
    ).Model
    return get_function_parameters(model_class.__init__)


def is_leaf(path: str):
    children = [u for u in [p for p in os.listdir(path)] if os.path.isdir(u)]
    return os.path.exists(os.path.join(path, "results")) or len(children) == 0


def get_leaves_rec(path: str):
    sub = [os.path.join(path, p) for p in os.listdir(path)]
    dirs = list(
        chain([get_leaves_rec(s)[0] for s in sub if os.path.isdir(s) if not "__" in s])
    )
    return dirs if not is_leaf(path) else [path]


def get_parameters(path: str, dataset: str = "default"):
    # leaves = get_leaves_rec(path)
    config = os.path.join(path, "parameters", f"{dataset}.json")
    if os.path.exists(config):
        with open(config) as f:
            result = json.load(f)
        return result
    else:
        return get_model_parameters(path)

    # result = [
    #    (leaf.replace("/", "."), get_model_parameters(leaf)) for leaf in leaves
    # ]
    # return result


if __name__ == "__main__":
    print(get_parameters("ciao"))
