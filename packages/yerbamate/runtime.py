import os
import json
import ipdb

class MateRuntime:
    def save(self):
        data = {k: v for k, v in self.__dict__.items() if not k.startswith("__")}
        with open(self.__runtime_save_path, "w") as f:
            json.dump(data, f)

    def __init__(self, *, command: str, runtime_save_path: str):
        self.command = command
        self.__runtime_save_path = runtime_save_path
