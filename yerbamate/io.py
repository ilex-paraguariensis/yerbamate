

import os
import json
import shutil
import sys
from yerbamate.bunch import Bunch


def set_save_path(root_save_folder: str, root_folder: str, model_name: str, params: str):
    save_path = os.path.join(
        root_save_folder, "models", model_name, "results", params
    )
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # save parameters in results folder
    hparams_source_file_name = os.path.join(
        root_folder,
        "models",
        model_name,
        "hyperparameters",
        f"{params}.json",
    )
    hparams_destination_file_name = os.path.join(
        save_path, "train_parameters.json"
    )
    shutil.copy(hparams_source_file_name, hparams_destination_file_name)
    return save_path


def override_params(config: Bunch, params: Bunch):
    if "override_params" in config and config.override_params.enabled:
        for key, value in config.override_params.items():
            if key == "enabled":
                key = "override_params"
            params[key] = value
    return params


def read_hyperparameters(conf: Bunch, root_folder: str,  model_name: str, hparams_name: str = "default"):
    with open(
        os.path.join(
            root_folder,
            "models",
            model_name,
            "hyperparameters",
            f"{hparams_name}.json",
        )
    ) as f:
        hparams = json.load(f)
        env_location = os.path.join(
            root_folder,
            "env.json",
        )
    if not os.path.exists(env_location):
        print(f"Could not find env.json in {env_location}. Created one.")
        with open(env_location, "w") as f:
            json.dump({}, f)

    with open(env_location) as f:
        env = json.load(f)

    env_in_params = [
        (key, val) for key, val in hparams.items() if key.startswith("env.")
    ]
    modified_env = False
    for key, val in env_in_params:
        stripped_key = key[4:]
        if key not in env:
            env[stripped_key] = val
            modified_env = True
        hparams[stripped_key] = env[stripped_key]
        hparams.pop(key, None)

    if modified_env:
        with open(env_location, "w") as f:
            json.dump(env, f, indent=4)
        print("Updated env.json")
        print(json.dumps(env, indent=4))

    hparams = Bunch(hparams)
    hparams = override_params(conf, hparams)
    hparams = override_run_params(conf, hparams)
    print(json.dumps(hparams, indent=4))

    # trick to save parameters, otherwise changes are not saved after return!
    hparams = Bunch(json.loads(json.dumps(hparams)))

    return hparams


def override_run_params(config: Bunch, run_params: dict):

    # run params is a key value pair of parameters to override
    # keys are formatted as "model.parameters.lr"
    # values are the new values
    # we need to override the config with the new values

    if run_params == None:
        return config

    def update_dict_in_depth(d: dict, keys: list, value):
        if len(keys) == 1:
            d[keys[0]] = value
        else:
            update_dict_in_depth(d[keys[0]], keys[1:], value)

    for key, value in run_params.items():
        keys = key.split(".")
        if len(keys) == 1:
            config[keys[0]] = value

        else:
            update_dict_in_depth(config, keys, value)

    return config


def find_root():
    """
    Method in charge of finding the root folder of the project and reading the content of mate.json
    """
    # path of execution
    current_path = os.getcwd()
    found = False
    i = 0
    while not found and i < 6:

        if os.path.exists(os.path.join(current_path, "mate.json")):
            conf_path = os.path.join(current_path, "mate.json")
            config = load_mate_config(conf_path)
            root_folder = config.project
            # self.__import_submodules(self.root_folder)
            found = True
        else:
            os.chdir("..")
            current_path = os.getcwd()
            i += 1
            if current_path == "/" or i == 6:
                print("ERROR: Could not find mate.json")
                sys.exit(1)

    # self.root_save_folder = self.root_folder
    sys.path.insert(0, os.getcwd())
    return root_folder, config


def list_packages(root_folder: str, folder: str):
    return (
        tuple(
            x
            for x in os.listdir(os.path.join(root_folder, folder))
            if not "__" in x
        )
        if os.path.exists(os.path.join(root_folder, folder))
        else tuple()
    )


def load_mate_config(path):
    with open(path) as f:
        config = Bunch(json.load(f))
        assert (
            "results_folder" in config
        ), 'Please add "results_folder":<path> in mate.json'
        assert (
            "project" in config
        ), 'Please add "project":<project name> in mate.json'
    return config