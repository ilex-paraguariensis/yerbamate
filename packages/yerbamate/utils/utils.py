import inspect
from typing import Callable
import ipdb
import os
from itertools import chain
import json

from .bunch import Bunch


def once(func):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return func(*args, **kwargs)

    wrapper.has_run = False
    return wrapper


print_once = once(print)


def get_function_parameters(
    function: Callable,
    object: dict,
    generate_defaults: bool = False,
    generate_none: bool = False,
):

    default = {}
    if "params" in object:
        params = object["params"].copy()
    else:
        params = {}

    error = None

    for param_name, param in inspect.signature(function).parameters.items():

        # only add parameters that are not self or exist in the params
        if param_name in params or param_name == "self":
            continue

        # only allow named parameters and not *args or **kwargs
        if param.kind != param.POSITIONAL_OR_KEYWORD:
            continue

        if param.default is not param.empty:
            # ignore None values
            if param.default != None and generate_defaults:
                default[param_name] = param.default
            elif generate_none:
                default[param_name] = None

        elif param.annotation is not param.empty:
            default[param_name] = f"Fix me! {param.annotation}"
            error = f"Missing parameter {param_name} for {object['module']}\nHint: {param.annotation}"
        else:
            default[param_name] = "Fix me!"
            error = f"Missing parameter {param_name} for {object['module']}\nHint: Add a default value or type annotation"

    params.update(default)

    return params, error


def migrate_mate_version(config: Bunch, root_project: str):

    from yerbamate import __version__
    from . import migrator

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
