from yerbamate.packages.metadata.metadata import BaseMetadata, Metadata
from .utils.bunch import Bunch
from .backbone_type import BackboneType
from enum import Enum
from typing import Any
import json
import ipdb


class Config:
    def __init__(self, config: Bunch):

        if "metadata" in config:
            config["metadata"] = Metadata(**config["metadata"])
        # ipdb.set_trace()

        for key, value in self.__dict__.items():
            if value != None and value != {}:
                assert key in config, f"Missing key {key} in config"
            if isinstance(value, Enum):
                enum_type = type(value)
                assert (
                    config[key] in enum_type.__members__.keys()
                ), "Invalid value for key {key}, must be one of {enum_type.__members__.keys()}"
                config[key] = type(value)(config[key])
            assert isinstance(config[key], type(value)), f"Wrong type for key {key}"
            setattr(self, key, config[key])
        for key in config.keys():
            assert key in self.__dict__.keys(), f"Unknown key {key} in config."

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


class MateConfig(Config):
    def __init__(self, config):
        self.project = ""
        self.mate_version = ""
        self.results_folder = ""
        # self.backbone: BackboneType = BackboneType.lightning
        self.override_params: dict[str, Any] = {}
        self.metadata: BaseMetadata = BaseMetadata()
        super().__init__(config)
