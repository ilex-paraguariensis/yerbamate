"""
a class that writes and reads from a cache file in json format
"""
import json
import os


class Cache:
    def __init__(self, path):
        self.path = os.path.join(path, "mate.cache")
        self.read()

    def __write(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f)

    def read(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def get(self, key, default):
        if key in self.data:
            return self.data[key]
        else:
            return default

    def set(self, key, value):
        self.data[key] = value
        self.__write()

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, key):
        return key in self.data

    def __str__(self):
        return json.dumps(self.data, indent=4)

    def __dir__(self):
        return self.data.keys()

    def __getattr__(self, key):
        try:
            return self.data[key]
        except KeyError:
            raise AttributeError(key)


# export the cache class
__all__ = ["cache"]
