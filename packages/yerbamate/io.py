import json
import os
import shutil
import sys
from typing import Optional
import ipdb
from .mate_config import MateConfig
from .utils.utils import once
from typing import Any


def set_save_path(root_save_folder: str, root_folder: str, params: str):
    save_path = os.path.join(root_save_folder, root_folder, params)

    return save_path


def save_train_experiments(save_path, hparams: dict[str, Any], conf: MateConfig):
    params = hparams.copy()
    params["mate"] = conf.copy()
    with open(os.path.join(save_path, "train.json"), "w") as f:
        json.dump(params, f, indent=4)


def update_experiments(
    root_folder: str, model_name: str, params: str, hparams: dict[str, Any]
):
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


def override_params(config: MateConfig, params: dict[str, Any]):

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


def get_metadata_path(root_folder: str, experiment: str):
    path = os.path.join(root_folder, "experiments", experiment, "metadata.json")
    # os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def save_metadata(root_folder: str, experiment: str, metadata: dict):
    path = get_metadata_path(root_folder, experiment)
    with open(path, "w") as f:
        json.dump(metadata, f, indent=4)


def save_toml(root_folder: str, experiment: str, toml: str):
    path = os.path.join(root_folder, "experiments", experiment, "experiment.toml")
    with open(path, "w") as f:
        f.write(toml)


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


def apply_env(root_folder: str, hparams: dict[str, Any]):
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


def override_run_params(hparams: dict[str, Any], run_params: dict):

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


def find_root() -> tuple[str, MateConfig]:
    """
    Method in charge of finding the root folder of the project and reading the content of mate.json
    """
    # path of execution
    current_path = os.getcwd()
    found = False
    i = 0
    root_folder = ""
    config: Optional[MateConfig] = None
    while not found:

        if os.path.exists(os.path.join(current_path, "mate.json")):
            conf_path = os.path.join(current_path, "mate.json")
            config = MateConfig(conf_path)
            assert config is not None, f"Error initializing mate config {conf_path}"
            root_folder = current_path
            found = True
            os.chdir("..")
        else:
            os.chdir("..")
            current_path = os.getcwd()
            i += 1
            if current_path == "/" or i == 6:
                raise Exception(
                    "Could not find mate.json. Please make sure you are in the root folder of the project."
                )
    sys.path.insert(0, os.getcwd())
    assert config is not None
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
