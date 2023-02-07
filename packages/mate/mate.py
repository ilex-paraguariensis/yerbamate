
import json
import os
import shutil
import sys
import ipdb


ENV_KEY = "env"

class Mate(dict):

    def __init__(self):
        

        # default restart, test to False
        self.restart = False
        self.test = False
        self.train = False
        self.sample = False
        self.hparams = {}
        # set major command to True
        setattr(self, sys.argv[1], True)

        self._root = self.__find_root()

        # set attributes based on the command line arguments
        for arg in sys.argv:
            if "=" not in arg:
                continue
            key, value = arg.split("=")
            value = self.convert_str_to_data(value)
            setattr(self, key, value)
            self.hparams[key] = value
        self._path = sys.argv[0]
        # ipdb.set_trace()
        if "bin/mate" in self._path:
            self.name = os.path.join(*sys.argv[2:4])
            self._path = os.path.join(self._root, "experiments", sys.argv[2],  sys.argv[3] + ".py")
            # detect path to experiment
        else:
            self.name = self._path.split("/")[-2:]
            self.name = os.path.join(*self.name)[: -3]
        self.__set_env()
        # ipdb.set_trace()

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
        results =["results", "results_path", "results_dir", "save", "save_path", "save_dir"]
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
            with open(env_path, "w") as f:
                json.dump(conf[ENV_KEY], f)

        env = json.load(open(env_path, "r"))
        for key, value in conf[ENV_KEY].items():
            if not key in env:
                print(f"Environment variable {key} not found, setting to default: {value}")
                env[key] = value
        
        # automatically append experiment name to results path
        search_results = ["results", "results_path", "results_dir", "save", "save_path", "save_dir"]
        for key in search_results:
            if key in env:
                env[key] = os.path.join(env[key], *self.name.split("/"))
                # ipdb.set_trace()
                break

        setattr(self, "env", env)
    """
    Unknown keys default to False
    """
    def __getitem__(self, __key):
        if not __key in self:
            return False
        return super().__getitem__(__key)

 