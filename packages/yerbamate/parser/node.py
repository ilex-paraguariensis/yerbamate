from re import S
from typing import Optional, Any, Callable, Type, Union
import json

import regex as re

from ..utils.bunch import Bunch
import random
import ipdb

SimpleType = Union[str, int, float, bool, None]


class Node:
    object_key: Optional[str] = None
    _py_object: Optional[object] = None

    def __init__(self, args, parent=None, **kawrgs) -> None:
        self._original_keys = args.keys()
        if args is None:
            args = self._json()
        for key, val in args.items():
            setattr(self, key, val)

    def _get_python_object(self) -> object:
        pass

    @staticmethod
    def set_config(base_module: str, root_module: str, key_value_map: dict):
        Node._base_module = base_module
        Node._root_module = root_module
        Node._key_value_map = key_value_map

    def load_dynamic_objects(self):
        for key, value in self.__dict__.items():
            if type(value) == str and re.search(r"{.*}", value):
                # get the key name
                key_name = re.search(r"{.*}", value).group(0)[1:-1]

                dynamic_object = Node._key_value_map[key_name]
                setattr(self, key, dynamic_object)

            if type(value) == list:
                for i, item in enumerate(value):
                    if type(item) == str and re.search(r"{.*}", item):
                        # get the key name
                        key_name = re.search(r"{.*}", item).group(0)[1:-1]

                        dynamic_object = Node._key_value_map[key_name]
                        value[i] = dynamic_object

        # return object

    def post_object_creation(self):
        # ipdb.set_trace()
        if "object_key" in self._original_keys:
            Node._key_value_map[self.object_key] = self._py_object

    def load_module(self):

        assert "module" in self.__dict__, "module not found"

        fromlist = [self.class_name] if hasattr(self, "class_name") else []
        fromlist = [getattr(self, "class")] if hasattr(self, "class") else fromlist

        if hasattr(self, "function") and not hasattr(self, "class_name"):
            fromlist = [self.function]

        module_list = [
            Node._base_module + "." + self.module,
            Node._root_module + "." + self.module,
            self.module,
        ]

        for module in module_list:
            try:
                module = __import__(module, fromlist=fromlist)
                break
            except ModuleNotFoundError:
                pass

        if module == None:
            raise ModuleNotFoundError(f"module {module} not found")

        if "class_name" in self.__dict__:
            module = getattr(module, self.class_name)
        # if "class_name" in self:
        #     module = getattr(module, getattr[self, "class_name"])

        return module

    def _json(self):
        # returns a simple json representing the node (filtering out private properties and methods)

        def to_json(obj):
            if isinstance(obj, Node):
                return {
                    key: to_json(val)
                    for key, val in obj.__dict__.items()
                    if not key.startswith("_")
                    and not callable(val)
                    and type(val) in [str, int, float, bool, dict]
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
            if not key.startswith("_") and not callable(val) and type(val) != object
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

    def __load__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):

        if self._py_object != None:
            return self._py_object
        else:

            super_dict = self.__dict__
            super_dict = dict(
                {
                    key: val() if isinstance(val, Node) else val
                    for key, val in super_dict.items()
                    if not key.startswith("_") and key in self._original_keys
                }
            )
            return super_dict

    # def __dict__(self):
    #     super_dict = super().__dict__
    #     return dict({key: val for key, val in super_dict.items() if not key.startswith("_")})


class NodeDict(Node):
    def __init__(self, args, **kawrgs) -> None:
        assert type(args) == dict or type(args) == Bunch
        super().__init__(args, **kawrgs)

    def __load__(self, parent: Optional[Node] = None):

        # ipdb.set_trace()
        node_key_dict = {}
        for key, val in self.__dict__.items():

            if not key.startswith("_") and key in self._original_keys:
                val = load_node(val, parent=self)
                if isinstance(val, Node):
                    val.__load__(self)
                    setattr(self, key, val)
                    node_key_dict[key] = val
                elif isinstance(val, list):
                    for i, item in enumerate(val):
                        item = load_node(item, parent=self)
                        if isinstance(item, Node):
                            item.__load__(self)
                            val[i] = item()

        for key, val in node_key_dict.items():
            setattr(self, f"{key}_node", val)

        # self.load_dynamic_objects()

        return self

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        # ipdb.set_trace()
        # for key, val in self.__dict__.items():
        #     if isinstance(val, Node):
        #         setattr(self, key, val())
        self.load_dynamic_objects()
        result = {
            key: val if not isinstance(val, Node) else val()
            for key, val in self.__dict__.items()
            if not key.startswith("_") and key in self._original_keys
        }
        return result


class ObjectReference(Node):
    reference_key: str = ""
    _reference: Optional[Node] = None

    def __init__(self, args, parent: Optional[Node] = None, **kawrgs) -> None:
        super().__init__(args, parent=parent, **kawrgs)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return Node._key_value_map[self.reference_key]


class MethodCall(ObjectReference):
    function_call: str = ""
    reference_key: Optional[str] = None
    params: Bunch = Bunch({})

    def __call__(self, parent: Optional[object] = None, *args, **kwargs):

        if self._py_object != None:
            return self._py_object

        # first create DictNode of params
        dictNode = NodeDict(self.params)
        dictNode.__load__(self)
        params = dictNode()
        # print("method call params", params)

        # then call the function
        object = Node._key_value_map[self.reference_key]
        function = getattr(object, self.function_call)
        self._py_object = function(**params)
        self.post_object_creation()
        return self._py_object

    def __init__(self, args, parent: Optional[object] = None):
        super().__init__(args)


class YetAnotherMethodCall(MethodCall):
    function: str = ""
    object_key: str = ""
    params: Bunch = Bunch({})

    def __call__(self, parent: Optional[object] = None, *args, **kwargs):

        if self._py_object != None:
            return self._py_object

        # first create DictNode of params
        dictNode = NodeDict(self.params)
        dictNode.__load__(self)
        params = dictNode()
        # print("method call params", params)
        # ipdb.set_trace()

        # then call the function
        object = Node._key_value_map[self.reference_key]
        function = getattr(object, self.function)
        self._py_object = function(**params)
        self.post_object_creation()
        return self._py_object

    def __init__(self, args, parent: Optional[object] = None):
        super().__init__(args)


# Methodcall for objects
class AnonMethodCall(Node):
    function: str = ""
    params: Bunch = Bunch({})

    def __load__(self, parent=None) -> object:

        self._node = NodeDict(self.params)
        return self

    def __call__(self, *args, **kwargs):
        return self._node()


class FunctionModuleCall(Node):
    function: str = ""
    module: str = ""
    params: Bunch = Bunch({})
    method_args: Optional[list[AnonMethodCall]] = None

    def __load__(self, parent=None) -> object:

        self._param_node = NodeDict(self.params)
        self._param_node.__load__(self)
        return self

    def __call__(self):

        params = self._param_node()

        module = self.load_module()

        function = getattr(module, self.function)

        _arg, _kwarg = flatten_nameless_params(params)

        if _arg:
            self._py_object = function(*_arg, **_kwarg)
        else:
            self._py_object = function(**params)
        self.post_object_creation()
        return self._py_object

    def call_method(self, method_name: str, *args, **kwargs):
        method_arg_names = [arg["function"] for arg in self.method_args]
        assert method_name in method_arg_names

        idx = method_arg_names.index(method_name)
        method_args = self.method_args[idx]["params"]

        method_args = load_node(method_args, parent=self)
        # ipdb.set_trace()
        method_args.__load__(self)
        method_args = method_args()
        f, p = flatten_nameless_params(method_args)

        method = getattr(self._py_object, method_name)
        return method(*args, *f, **p, **kwargs)


def flatten_nameless_params(params: dict) -> dict:

    flat = params.pop("", None)
    flats = []
    while flat != None:
        flats.append(flat)
        flat = params.pop("", None)

    return flats, params


class Object(Node):
    module: str = ""
    class_name: str = ""
    params: Bunch = Bunch({})  # param is actualy a dictnode
    method_args: Optional[list[AnonMethodCall]] = None

    def __load__(self, parent: Optional[object] = None) -> object:

        if self._py_object != None:
            return self._py_object

        self.param_node = NodeDict(self.params)

        self.param_node.__load__()

        # ipdb.set_trace()

        return self

    def __call__(self, *args, **kwargs):

        if self._py_object != None:
            return self._py_object

        # ipdb.set_trace()

        module = self.load_module()

        self._py_object = module(**self.param_node())
        self.post_object_creation()
        return self._py_object

    def __init__(self, args: Optional[Bunch], parent: Optional[object] = None):
        super().__init__(args, parent=parent)

    def call_method(self, method_name: str, *args, **kwargs):
        # ipdb.set_trace()
        method_arg_names = [arg["function"] for arg in self.method_args]
        assert method_name in method_arg_names

        idx = method_arg_names.index(method_name)
        method_args = self.method_args[idx]["params"]

        # ipdb.set_trace()

        method_args = load_node(method_args, parent=self)
        method_args.__load__(self)
        method_args = method_args()

        method = getattr(self._py_object, method_name)
        return method(*args, **method_args, **kwargs)


class AnnonymousObject(Node):
    def __init__(self, args: Optional[dict] = None) -> None:
        super().__init__(args)
        setattr(self, "", "")


node_types: list[Type] = [
    Object,
    MethodCall,
    FunctionModuleCall,
    ObjectReference,
    AnonMethodCall,
    NodeDict,
]
SyntaxNode = Union[
    Object, FunctionModuleCall, MethodCall, ObjectReference, AnonMethodCall, NodeDict
]


def load_node(args, parent=None):
    if isinstance(args, dict):
        # ipdb.set_trace()
        node: Optional[SyntaxNode] = None
        for node_type in node_types:
            if node_type.is_one(args):
                node = node_type(args, parent=parent)
                return node

    return args
