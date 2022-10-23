from asyncio import subprocess
from enum import Enum
import json
from typing import Union
import ipdb
from git import Repo
from git.exc import InvalidGitRepositoryError
import warnings
import subprocess
from subprocess import check_output
import os

primitary_types = [int, float, str, bool, list, dict, tuple]
P_Types = Union[int, float, str, bool, list, dict, tuple]


def is_git_repo(path="."):
    return (
        subprocess.call(
            ["git", "-C", path, "status"],
            stderr=subprocess.STDOUT,
            stdout=open(os.devnull, "w"),
        )
        == 0
    )


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
        self.hash: str = ""
        self.type: str = ""
        self.exports: dict = {}
        self.history_url: list[str] = []

        for key, value in self.__dict__.items():
            if key in kwargs:
                setattr(self, key, kwargs[key])

        self.set_url()
        # ipdb.set_trace()

    def __str__(self):
        return json.dumps(
            {
                key: (val if isinstance(val, P_Types) else str(val))
                for key, val in self.__dict__.items()
            },
            indent=4,
        )

    def contains(self, key):
        return key in self.__dict__.keys()

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
            key: (val if isinstance(val, P_Types) else str(val))
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

    def get(self, key, default=None):
        if key in self.__dict__.keys():
            return getattr(self, key)
        else:
            return default

    def parse_url_from_git(self, path="."):
        assert is_git_repo(path), f"Not a git repository: {path=}"
        url = (
            check_output(["git", "config", "--get", "remote.origin.url"], cwd=path)
            .decode("utf-8")
            .strip()
        )
        return url

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)


class Metadata(BaseMetadata):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# class ModelMetadata(BaseMetadata):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         assert self.type == "model", "Wrong type for model metadata"
