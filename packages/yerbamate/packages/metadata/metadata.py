from enum import Enum
import json
import ipdb


class BaseMetadata(dict):
    def __init__(self, **kwargs):
        self.name: str = ""
        self.description: str = ""
        self.version: str = ""
        self.author: str = ""
        self.license: str = ""
        self.url: str = ""
        self.version: str = ""
        self.category: str = ""
        self.backbone: str = ""

        for key, value in self.__dict__.items():
            if key in kwargs:
                setattr(self, key, kwargs[key])

        # ipdb.set_trace()

    def __str__(self):
        return json.dumps(
            {
                key: (val if not isinstance(val, Enum) else str(val))
                for key, val in self.__dict__.items()
            },
            indent=4,
        )

    def __repr__(self):
        return self.__str__()

    def __json__(self):
        return self.to_dict()

    def add(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            key: (val if not isinstance(val, Enum) else str(val))
            for key, val in self.__dict__.items()
        }

    def copy(self):
        return BaseMetadata(**self.to_dict().copy())


class Metadata(BaseMetadata):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# class ModelMetadata(BaseMetadata):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         assert self.type == "model", "Wrong type for model metadata"
