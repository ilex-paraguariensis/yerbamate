from typing import Optional, Any, Callable, Type, Union
import json
from .bunch import Bunch
import random
import ipdb


class Node:

    object_key: Optional[str] = None
    _py_object: Optional[object] = None

    def __init__(self, args: Optional[dict] = None) -> None:
        if args is None:
            args = self._json()
        for key, val in args.items():
            setattr(self, key, val)

        if self.object_key is None:
            self.object_key = "_rnd_" + "".join(  # it will start with
                random.choice("0123456789abcdef") for n in range(25)
            )

    def _get_python_object(self) -> object:
        pass

    def _json(self):
        # returns a simple json representing the node (filtering out private properties and methods)

        def to_json(obj):
            if isinstance(obj, Node):
                return {
                    key: to_json(val)
                    for key, val in obj.__dict__.items()
                    if not key.startswith("_") and not callable(val)
                }
            elif isinstance(obj, list):
                return [to_json(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: to_json(val) for key, val in obj.items()}
            else:
                return obj

        return to_json(self)

    def __str__(self):
        return json.dumps(self._json(), indent=4)

    def __repr__(self):
        return str(self)

    @classmethod
    def _base_json(cls):
        # returns a simple json representing the node (filtering out private properties and methods)
        cur_params = {
            key: val
            for key, val in cls.__dict__.items()
            if not key.startswith("_") and not callable(val)
        }
        for base_class in cls.__bases__:
            if base_class != object:
                cur_params |= {
                    key: val
                    for key, val in base_class.__dict__.items()
                    if not key.startswith("_")
                    and not callable(val)
                    and not (hasattr(val, "__get__") and callable(val.__get__))
                }
        return cur_params

    @classmethod
    def is_one(cls: Type, obj: Any) -> bool:
        # checks that the given object has the same property as the current node
        """
        return isinstance(obj, dict) and (
            sorted(list(obj.keys())) == node_properties
        )
        """
        if not isinstance(obj, dict):
            return False
        for key, val in cls._base_json().items():
            if key not in obj and val is not None:
                return False
        return True

    @classmethod
    def assert_is_one(cls: Type, obj: Any):
        if not cls.is_one(obj):
            raise SyntaxError(
                f"Object {obj} is not a valid node Node. \n This is how it should look like:\n{cls._base_json()}"
            )


class ObjectReference(Node):
    reference_key: str = ""
    _reference: Optional[Node] = None

    def __init__(self, args):
        super().__init__(args)


class MethodCall(ObjectReference):
    function_call: str = ""
    reference_key: Optional[str] = None
    params: Bunch = Bunch({})

    def __call__(self, *args, **kwargs):
        return getattr(self._py_object, self.function_call)(
            *args, **(self.params | kwargs)
        )

    def __init__(self, args, parent: Optional[object] = None):
        super().__init__(args)


class Object(Node):
    module: str = ""
    class_name: str = ""
    params: Bunch = Bunch({})
    method_args: Optional[dict[str, MethodCall]] = None

    def _load(self):
        if self._py_object is not None:
            class_val = self._load_module()
            loaded_params = {}
            for key, val in self.params.items():
                if isinstance(val, Object):
                    val._load()
                    loaded_params[key] = val._py_object
                elif isinstance(val, MethodCall):
                    loaded_params[key] = val()
                elif isinstance(val, ObjectReference):
                    val._reference._load()
                    loaded_params[key] = val._reference._py_object

            self._py_object = class_val(
                **{
                    key: (
                        val
                        if not hasattr(val, "reference_key")
                        else val._reference
                    )
                    for key, val in self.params.items()
                }
            )

    def _load_module(self) -> Type:
        fromlist = self.class_name
        base_module = self.module
        module = None
        for _ in range(3):
            try:
                module = __import__(base_module, fromlist=fromlist)
                break
            except ModuleNotFoundError:
                base_module = ".".join(base_module.split(".")[1:])
        if module is None:
            raise ModuleNotFoundError(f"Could not find module {self.module}")

        return getattr(module, self.class_name)

    def __init__(self, args: Optional[Bunch] = None):
        super().__init__(args)
        # the the object_key is not set, we generate a random one


class LRScheduler(Node):
    monitor: str = ""
    scheduler: Object = Object()  # initialize it because its mandatory

    def __init__(
        self,
        args: Optional[Bunch] = None,
    ) -> None:
        super().__init__(args)
        if args is not None:
            Object.assert_is_one(self.scheduler)
            self.scheduler = Object(self.scheduler)


class Optimizers(Node):
    optimizer: Object = Object()  # initialize it because its mandatory
    lr_scheduler: LRScheduler = LRScheduler()

    def __init__(self, params):
        super().__init__(params)


node_types: list[Type] = [
    Object,
    MethodCall,
    ObjectReference,
    LRScheduler,
    Optimizers,
]
SyntaxNode = Union[
    Object, MethodCall, ObjectReference, LRScheduler, Optimizers
]
