from types import SimpleNamespace

import json


class Bunch(dict):
    def __init__(self, keyvals: dict):
        for key, val in keyvals.items():
            self.__dict__[key] = val if not isinstance(val, dict) else Bunch(val)
        self.__dict__ = self


class Bunch(dict):
    def __init__(self, kwargs):
        super().__init__(kwargs)
        for key, val in kwargs.items():
            self.__dict__[key] = val if not isinstance(val, dict) else Bunch(val)

    def to_dict(self):
        proto = self.__dict__.copy()
        for key, val in proto.items():
            proto[key] = val if not isinstance(val, Bunch) else val.to_dict()
        return proto

    def contains(self, key):
        return key in self.keys()

    def has(self, key):
        return self.contains(key)

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)

    def __setattr__(self, key, value):
        self[key] = value

    def __dir__(self):
        return self.keys()

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setstate__(self, state):
        # Bunch pickles generated with scikit-learn 0.16.* have an non
        # empty __dict__. This causes a surprising behaviour when
        # loading these pickles scikit-learn 0.17: reading bunch.key
        # uses __dict__ but assigning to bunch.key use __setattr__ and
        # only changes bunch['key']. More details can be found at:
        # https://github.com/scikit-learn/scikit-learn/issues/6196.
        # Overriding __setstate__ to be a noop has the effect of
        # ignoring the pickled __dict__
        pass
