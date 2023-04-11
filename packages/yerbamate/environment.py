
import json
import os
import shutil
import sys
import ipdb


ENV_KEY = "env"


class Environment(dict):

    def __init__(self):

        # default restart, test to False
        self.restart = False
        self.test = False
        self.train = False
        self.sample = False
        self.hparams = {}

        # set command to True
        try:
            setattr(self, sys.argv[1], True)
        except:
            pass

        self._root = self.__find_root()

        # parse python -m module train arg=1 arg2=2
        for arg in sys.argv:
            if "=" not in arg:
                continue
            key, value = arg.split("=")
            value = self.convert_str_to_data(value)
            setattr(self, key, value)
            self.hparams[key] = value

        self._path = sys.argv[0]
        if "bin/mate" in self._path:
            self.name = os.path.join(*sys.argv[2:4])
            self._path = os.path.join(
                self._root, "experiments", sys.argv[2],  sys.argv[3] + ".py")
            # detect path to experiment
        else:
            self.name = self._path.split("/")[-2:]
            self.name = os.path.join(*self.name)[: -3]

        self.__set_env()

        if self.train:
            self.__generate_experiment()

    def convert_str_to_data(self, input):
        try:
            return int(input)
        except ValueError:
            try:
                return float(input)
            except ValueError:
                if input in ["True", "true"]:
                    return True
                elif input in ["False", "false"]:
                    return False

        return input

    def __find_root(self):
        # TODO, find root of the project

        path = os.getcwd()

        if os.path.exists(os.path.join(path, "mate.json")):
            conf = json.load(open(os.path.join(path, "mate.json"), "r"))

            return os.path.join(path, conf["project"])

        return None

    def __generate_experiment(self):
        # copies the experiment to the results folder
        results = ["results", "results_path",
                   "results_dir", "save", "save_path", "save_dir"]
        result = None
        for key in results:
            if key in self.env:
                result = self.env[key]
                break
        if result is None:
            return
        if not os.path.exists(result):
            os.makedirs(result)

        save_file = os.path.join(result, "experiment.py")
        # copy from self._path to save_file
        shutil.copyfile(self._path, save_file)

        # ipdb.set_trace()

        if self.hparams != {}:
            params_file = os.path.join(result, "experiment.json")
            # dump self to params
            # overwrite if exists
            with open(params_file, "w") as f:
                json.dump(dict(self.hparams), f, indent=4)

    def __set_env(self):
        mate_conf_path = os.path.join("mate.json")
        conf = json.load(open(mate_conf_path, "r"))

        env_path = os.path.join("env.json")
        if not os.path.exists(env_path):
            print("Environment file not found, creating one with defaults: env.json")

            if ENV_KEY in conf:
                required_keys = conf[ENV_KEY].keys()
            else:
                required_keys = ["results"]

            defualt_env = {key: "" for key in required_keys}

            with open(env_path, "w") as f:
                json.dump(defualt_env, f, indent=4)

        with open(env_path, "r") as f:
            try:
                env = json.load(f)
            except json.decoder.JSONDecodeError:
                env = {
                    "results": "",
                }

        env_not_found = []

        if ENV_KEY in conf:
            for key, value in env.items():
                if env[key] == "":
                    if key in os.environ:
                        env[key] = os.environ[key]
                        # print(f"Environment variable {key} set to {os.environ[key]} from shell.")
                    else:
                        env_not_found.append(key)
                        env[key] = value

        if len(env_not_found) > 0:
            print(
                f"Environment variables not found. Set them in env.json or in your shell.")
            for key in env_not_found:
                desc = conf[ENV_KEY][key] if key in conf[ENV_KEY] else "Required environment variable"
                print(f"{key} : {desc}")

            print("Exiting...")
            sys.exit(1)

        # automatically append experiment name to results path
        search_results = ["auto_save"]
        for key in search_results:
            if key in env:
                env[key] = os.path.join(env[key], *self.name.split("/"))
                # env["results"] = env[key]
                break
            if os.environ.get(key, None) is not None and os.environ.get(key, None) != "":
                env[key] = os.environ.get(key)
                # env["results"] = env[key]
                break

        if len(env) == 0:
            print(
                f"results/save_dir/save environment variable is empty. Set it in env.json or in your shell.")
            print("Exiting...")
            sys.exit(1)

        setattr(self, "env", env)

    def __getitem__(self, key):
        if not key in self:
            # ipdb.set_trace()
            if key in self.env:
                return self.env[key]
            res = os.environ.get(key, None)

            if res is None or res == "":
                print(
                    f"Environment variable {key} not found. Set it in env.json or in your shell.")
                print("Exiting...")
                sys.exit(1)
            else:
                return res

        return super().__getitem__(key)
