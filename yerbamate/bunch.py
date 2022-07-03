from types import SimpleNamespace
import json

class Bunch(SimpleNamespace):
    def __init__(self, keyvals: dict):
        for key, val in keyvals.items():
            self.__dict__[key] = val if not isinstance(val, dict) else Bunch(
                keyvals
            )

    def to_dict(self):
        proto = self.__dict__.copy()
        for key, val in proto.items():
            proto[key] = val if not isinstance(val, Bunch) else val.to_dict()
        return proto


    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)
        
