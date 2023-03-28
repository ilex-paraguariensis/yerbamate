from types import SimpleNamespace

import json
import ipdb


class Bunch(dict):
    def __init__(self, dict):
        super().__init__(dict)

        self.__original_dict = dict

        for key, val in dict.items():
            self.__dict__[key] = val
            self.__setattr__(key, val)
        
        
        # for key, val in kwargs.items():
        #     self.__dict__[key] = val if not isinstance(val, dict) else Bunch(val)

    # def to_dict(self):
    #     proto = self.__dict__.copy()
    #     for key, val in proto.items():
    #         proto[key] = val if not isinstance(val, Bunch) else val.to_dict()
    #     return proto

    # def contains(self, key):
    #     return key in self.keys()

    # def has(self, key):
    #     return self.contains(key)

    # def is_empty(self):
    #     return len(self.keys()) == 0

    # def clone(self):
    #     return Bunch(self.to_dict())

    # def __str__(self):
    #     return json.dumps(self.to_dict(), indent=4, default=str)

    # def __setattr__(self, key, value):
    #     self.__setitem__(key, value)

    # def __dir__(self):
    #     return self.keys()

    # def __getattr__(self, key):
    #     return self.__getitem__(key)

    # def __setitem__(self, key, value):
    #     super().__setitem__(key, value)
    #     self.__dict__[key] = value

    # def __getitem__(self, key):
    #     if key in self.__dict__:
    #         return self.__dict__[key]
    #     else:
    #         if hasattr(self, key):
    #             return getattr(self, key)
    #     return super().__getitem__(key)

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
