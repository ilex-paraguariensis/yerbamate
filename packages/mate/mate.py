
import json
import os
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
        
        # set major command to True
        setattr(self, sys.argv[1], True)

        # set attributes based on the command line arguments
        for arg in sys.argv[2:]:
            key, value = arg.split("=")
            setattr(self, key[2:], value)
        self._path = sys.argv[0]
        self.name = self._path.split("/")[-2:]
        self.name = os.path.join(*self.name)[: -3]
        self.__set_env()
        # ipdb.set_trace()

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

 