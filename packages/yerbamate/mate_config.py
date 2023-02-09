from enum import Enum
from typing import Any
import json
import ipdb


class Config:
    def __init__(self, config: dict):
        for key, value in self.__dict__.items():
            if value != None and value != {}:
                # Why assert when we can just set the default value?
                setattr(self, key, value)
                # assert key in config, f"Missing key {key} in config"
            if isinstance(value, Enum):
                enum_type = type(value)
                assert (
                    config[key] in enum_type.__members__.keys()
                ), "Invalid value for key {key}, must be one of {enum_type.__members__.keys()}"
                config[key] = type(value)(config[key])
            if key in config:
                assert isinstance(config[key], type(value)), f"Wrong type for key {key}"
                setattr(self, key, config[key])

        # Disable this for now as its changing the config
        # for key in config.keys():
        #     assert key in self.__dict__.keys(), f"Unknown key {key} in config."

    def __str__(self):
        return json.dumps(
            {
                key: (val if not isinstance(val, Metadata) else val.to_dict())
                for key, val in self.__dict__.items()
            },
            indent=4,
        )

    def __repr__(self):
        return self.__str__()

    def json(self):
        return {
            key: (val if not isinstance(val, Enum) else str(val))
            for key, val in self.__dict__.items()
        }

    def copy(self):
        return self.json().copy()

    # add mate["item"] = "value" functionality
    def __setitem__(self, key, value):
        setattr(self, key, value)

    # add mate["item"] functionality
    def __getitem__(self, key):
        return getattr(self, key)


class MateConfig(Config):
    def __init__(self, config):
        self.project = ""
        self.mate_version = ""
        self.results_folder = ""
        self.override_params: dict[str, Any] = {}
        self.restarting = False
        
        super().__init__(config)

    def save(self, path="mate.json"):

        with open(path, "w") as f:
            f.write(self.__str__())
