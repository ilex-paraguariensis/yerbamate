import json
import os
import shutil
import sys
from typing import Optional
import ipdb

from .mate_config import MateConfig

from .utils.bunch import Bunch
from .utils.utils import once


def load_json(path):
    with open(path) as f:
        return Bunch(json.load(f))


def set_save_path(
    root_save_folder: str, root_folder: str, model_name: str, params: str
):
    # exp_path = __get_experiment_path(root_folder, model_name, params)
    exp_module = get_experiment_base_module(root_folder, model_name, params)

    if exp_module == root_folder:
        # model name is actually the experiment name
        save_path = os.path.join(
            root_save_folder, root_folder, "experiments", model_name
        )

    else:
        save_path = os.path.join(
            root_save_folder, root_folder, "models", model_name, "experiments", params
        )
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    return save_path


def save_train_experiments(save_path, hparams: Bunch, conf: MateConfig):
    params = hparams.copy()
    params["mate"] = conf.copy()
    with open(os.path.join(save_path, "train.json"), "w") as f:
        json.dump(params, f, indent=4)


def update_experiments(root_folder: str, model_name: str, params: str, hparams: Bunch):
    path = __get_experiment_path(root_folder, model_name, params)
    with open(
        os.path.join(
            root_folder,
            "models",
            model_name,
            "experiments",
            f"{params}.json",
        ),
        "w",
    ) as f:
        json.dump(hparams, f, indent=4)


def override_params(config: MateConfig, params: Bunch):

    # ipdb.set_trace()
    if (
        config.override_params is not None
        and "enabled" in config.override_params
        and config.override_params["enabled"]
    ):
        for key, value in config.override_params.items():
            if key == "enabled":
                key = "override_params"
            params[key] = value
    return params


def __get_experiment_path(root_folder: str, model_name: str, experiment_name: str):
    """
    if experiment == "default":
        # firt check if second level default exists
        path = os.path.join(
            root_folder, "models", model_name, "experiments", "default.json"
        )
        if os.path.exists(path):
            return path

        # if not, check if first level default exists
        path = os.path.join(root_folder, "experiments", f"{model_name}.json")
        if os.path.exists(path):
            return path

    path = os.path.join(
        root_folder, "models", model_name, "experiments", f"{experiment}.json"
    )
    """
    path = os.path.join(root_folder, "experiments", f"{experiment_name}.json")
    return path


def get_experiment_base_module(root_folder: str, model_name: str, experiment: str):

    if experiment == "default":
        # firt check if second level default exists
        if os.path.exists(
            os.path.join(
                root_folder, "models", model_name, "experiments", "default.json"
            )
        ):
            return ".".join([root_folder, "models", model_name])

        else:
            path = os.path.join(root_folder, "experiments", f"{model_name}.json")
            if os.path.exists(path):
                return root_folder

    # if not, check if first level default exists
    # ipdb.set_trace()
    module = ".".join([root_folder, "models", model_name])

    return module


print_once = once(print)


def apply_env(root_folder: str, hparams: Bunch):
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
        # print(json.dumps(env, indent=4))


def read_experiments(
    conf: MateConfig,
    root_folder: str,
    model_name: str,
    hparams_name: str = "default",
    run_params: dict = None,
):

    hparams_path = __get_experiment_path(root_folder, model_name, hparams_name)
    assert hparams_path != None, f"Could not find the experiment {model_name}"

    # exp = get_experiment_description(root_folder, model_name, hparams_name)
    # print_once(f"{exp[2]}: {exp[0]}/{exp[1]}.json")

    with open(hparams_path) as f:
        hparams = json.load(f)

    hparams = Bunch(hparams)
    hparams = override_params(conf, hparams)
    hparams = override_run_params(hparams, run_params)

    # trick to save parameters, otherwise changes are not saved after return!
    hparams = Bunch(json.loads(json.dumps(hparams)))

    return hparams


def override_run_params(hparams: Bunch, run_params: dict):

    # parsed from mate {command} --param1=value1 --param2=value2
    # run params is a key value pair of parameters to override
    # keys are formatted as "model.parameters.lr"
    # values are the new values
    # we need to override the config with the new values

    if run_params == None:
        return hparams

    def update_dict_in_depth(d: dict, keys: list, value):
        if len(keys) == 1:
            d[keys[0]] = value
        else:
            update_dict_in_depth(d[keys[0]], keys[1:], value)

    for key, value in run_params.items():
        keys = key.split(".")
        if len(keys) == 1:
            hparams[keys[0]] = value

        else:
            update_dict_in_depth(hparams, keys, value)

    return hparams


def find_root():
    """
    Method in charge of finding the root folder of the project and reading the content of mate.json
    """
    # path of execution
    current_path = os.getcwd()
    found = False
    i = 0
    root_folder = ""
    config : Optional[MateConfig] = None
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
                raise Exception(
                    "Could not find mate.json. Please make sure you are in the root folder of the project."
                )

    # self.root_save_folder = self.root_folder
    sys.path.insert(0, os.getcwd())
    return root_folder, config


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


def experiment_exists(root_folder: str, model_name: str, experiment_name: str):
    # ipdb.set_trace()
    exp_path = __get_experiment_path(root_folder, model_name, experiment_name)
    return os.path.exists(exp_path)


def assert_experiment_exists(root_folder: str, model_name: str, experiment_name: str):
    # ipdb.set_trace()
    exp_path = __get_experiment_path(root_folder, model_name, experiment_name)

    assert os.path.exists(exp_path), f"Experiment {exp_path} does not exist"


def load_mate_config(path):
    with open(path) as f:
        config = MateConfig(json.load(f))
        # assert (
        #    "results_folder" in config
        # ), 'Please add "results_folder":<path> in mate.json'
        # assert "project" in config, 'Please add "project":<project name> in mate.json'
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
