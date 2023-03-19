import json
import os
import shutil
import sys
from typing import Optional
import ipdb

from .....utils.bunch import Bunch
from .....utils.utils import once



print_once = once(print)


def find_root():
    """
    Method in charge of finding the root folder of the project and reading the content of mate.json
    """
    # path of execution
    current_path = os.getcwd()
    found = False
    i = 0
    root_folder = ""
    config = None
    while not found and i < 2:
        if os.path.exists(os.path.join(current_path, "mate.json")):
            conf_path = os.path.join(current_path, "mate.json")
            config = load_mate_config(conf_path)
            root_folder = config["project"]
            # self.__import_submodules(self.root_folder)
            found = True
        else:
            os.chdir("..")
            current_path = os.getcwd()
            i += 1
            if current_path == "/" or i == 2:
                raise Exception(
                    "Could not find mate.json. Please make sure you are in the root folder of the project."
                )

    # self.root_save_folder = self.root_folder
    sys.path.insert(0, os.getcwd())
    return root_folder, Bunch(config)


def decorator_dict_to_object(func):
    def wrapper(*args, **kwargs):
        return Bunch(func(*args, **kwargs))

    return wrapper


def list_packages(root_folder: str, folder: str):
    return (
        tuple(x for x in os.listdir(os.path.join(root_folder, folder)) if not "__" in x)
        if os.path.exists(os.path.join(root_folder, folder))
        else tuple()
    )


def get_experiment_description(root_folder: str, model_name: str, experiment: str):
    # ipdb.set_trace()
    experiments = list_experiments(root_folder, model_name, False)
    for exp in experiments:
        if exp[1] == experiment and exp[2] == model_name:
            return exp
        if exp[1] == model_name and exp[2] == "experiments":
            return exp
    return None


def list_experiments(root_foolder: str, model_name=None, log=True):
    """
    models = list_packages(root_foolder, "models")

    dirs = [
        (os.path.join(root_foolder, "experiments"), "experiments"),
    ]

    if model_name != None and model_name in models:
        models = [model_name]
        dirs = []

    for model in models:
        dirs.append((os.path.join(root_foolder, "models", model, "experiments"), model))

    experiments = []

    for dir, model in dirs:
        if os.path.exists(dir):
            files = os.listdir(dir)
            for file in files:
                if not "__" in file and ".json" in file:
                    experiments.append([dir, file.replace(".json", ""), model])

    if log:
        for (
            dir,
            param_file,
            model,
        ) in experiments:
            print(f"{model}: {dir} {param_file}")

    paths = [x[0] for x in experiments]
    names = [x[1] for x in experiments]
    models = [x[2] for x in experiments]

    return experiments
    """
    return os.listdir(os.path.join(root_foolder, "experiments"))


def list_experiment_names(root_folder: str, model_name: str):
    experiments = list_experiments(root_folder, None, False)
    return [x[1] for x in experiments]


# def experiment_exists(root_folder: str, model_name: str, experiment_name: str):
#     # ipdb.set_trace()
#     exp_path = __get_experiment_path(root_folder, model_name, experiment_name)
#     return os.path.exists(exp_path)


# def assert_experiment_exists(root_folder: str, model_name: str, experiment_name: str):
#     # ipdb.set_trace()
#     exp_path = __get_experiment_path(root_folder, model_name, experiment_name)

#     assert os.path.exists(exp_path), f"Experiment {exp_path} does not exist"


def load_mate_config(path):
    with open(path) as f:
        config = json.load(f)
        # assert (
        #    "results_folder" in config
        # ), 'Please add "results_folder":<path> in mate.json'
        # assert "project" in config, 'Please add "project":<project name> in mate.json'

    # for
    
    return config


def remove(root_folder: str, model_name: str):
    action = "go"
    while action not in ("y", "n"):
        action = input(f'Are you sure you want to remove model "{model_name}"? (y/n)\n')
    if action == "y":
        shutil.rmtree(os.path.join(root_folder, "models", model_name))
        print(f"Removed model {model_name}")
    else:
        print("Ok, exiting.")


def list(root_folder: str, folder: str):
    print("\n".join(tuple("\t" + str(m) for m in list_packages(root_folder, folder))))


def clone(root_folder: str, source_model: str, target_model: str):
    shutil.copytree(
        os.path.join(root_folder, "models", source_model),
        os.path.join(root_folder, "models", target_model),
    )


def snapshot(root_folder: str, model_name: str):

    if not os.path.exists(os.path.join(root_folder, "snapshots")):
        os.makedirs(os.path.join(root_folder, "snapshots"))

    snapshot_names = [
        name.split("__") for name in os.listdir(os.path.join(root_folder, "snapshots"))
    ]
    matching_snapshots = [name for name in snapshot_names if name[0] == model_name]
    max_version_matching = (
        max([int(name[1]) for name in matching_snapshots])
        if len(matching_snapshots) > 0
        else 0
    )
    snapshot_name = f"{model_name}__{max_version_matching + 1}"

    shutil.copytree(
        os.path.join(root_folder, "models", model_name),
        os.path.join(root_folder, "snapshots", snapshot_name),
    )
    print(f"Created snapshot {snapshot_name}")
