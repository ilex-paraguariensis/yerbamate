from enum import Enum
import json
import ipdb
from git import Repo
import warnings


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
        self.root_module: str = ""
        self.module_path: list[str] = []

        for key, value in self.__dict__.items():
            if key in kwargs:
                setattr(self, key, kwargs[key])

        self.set_url()
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
            if value == None:
                delattr(self, key)

    def to_dict(self):
        return {
            key: (val if not isinstance(val, Enum) else str(val))
            for key, val in self.__dict__.items()
        }

    def copy(self):
        return BaseMetadata(**self.to_dict().copy())

    def set_url(self):
        self.url = self.get_url()

    def get_url(self):
        if self.url != "":
            return self.url
        else:
            return self.parse_url_from_git()

    def parse_url_from_git(self, path="."):
        try:
            repo = Repo(path)

            url = repo.remotes.origin.url

            if url.startswith("git@"):
                url = url.replace("git@", "https://")
                url = url.replace(":", "/")
                url = url.replace(".git", "")
                url = url + "/"

            return url

        except Exception as e:
            warnings.warn(f"Error: {e} while trying to find root git repo")

        return ""


class Metadata(BaseMetadata):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# class ModelMetadata(BaseMetadata):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         assert self.type == "model", "Wrong type for model metadata"
