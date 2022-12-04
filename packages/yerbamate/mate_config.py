# from .api.data.metadata.metadata import BaseMetadata, Metadata
from enum import Enum
from typing import Any
import json
import ipdb


class Config:
    def __init__(self, config: dict | str | None = None):
        if isinstance(config, str):
            try:
                with open(config, "r") as f:
                    config = json.load(f)
            except Exception as e:
                print(f"Could not parse config: {config}")
                raise e
        elif config is None:
            config = {}
        # if "metadata" in config:
        #     config["metadata"] = Metadata(
        #         **config["metadata"], root_module=config.get("project", "")
        #     )
        assert isinstance(config, dict)
        for key, value in self.__dict__.items():
            if value is not None and value != {} and value != False:
                assert key in config, f"Missing key:'{key}' in config"
            if isinstance(value, Enum):
                enum_type = type(value)
                assert (
                    config[key] in enum_type.__members__.keys()
                ), f"Invalid value for key {key}, must be one of {enum_type.__members__.keys()}"
                config[key] = type(value)(config[key])
            if key in config:
                assert isinstance(config[key], type(value)), f"Wrong type for key {key}"
                setattr(self, key, config[key])

        for key in config.keys():
            assert key in self.__dict__.keys(), f"Unknown key {key} in config."

    def __str__(self):
        return json.dumps(
            {key: val for key, val in self.__dict__.items()},
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
        self.mate_version = ""
        self.results_folder = ""
        self.verbose = False
        super().__init__(config)

    def __str__(self):
        return "MateConfig:" + super().__str__()

    def __repr__(self):
        return self.__str__()

    def save(self, path="mate.json"):

        with open(path, "w") as f:
            f.write(self.__str__())
