from typing import Optional, Any, Callable, Type, Union
import json

import regex as re

from .bunch import Bunch
import random
import ipdb


class Node:
    object_key: Optional[str] = None
    _py_object: Optional[object] = None
    _parent = None

    def __init__(self, args, parent=None, **kawrgs) -> None:

        if args is None:
            args = self._json()
        for key, val in args.items():
            setattr(self, key, val)

        _parent = parent

        if self.object_key is None:
            self.object_key = "_rnd_" + "".join(  # it will start with
                random.choice("0123456789abcdef") for n in range(25)
            )

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
                # replace the value
                dynamic_object = value.replace(
                    "{" + key_name + "}", Node._key_value_map[key_name]
                )
                setattr(self, key, dynamic_object)

        # return object

    def post_object_creation(self):
        if "object_key" in self.__dict__:
            Node._key_value_map[self.object_key] = self._py_object

    def load_module(self):

        assert "module" in self.__dict__, "module not found"

        fromlist = [self.class_name] if hasattr(self, "class_name") else []
        fromlist = [getattr(self, "class")] if hasattr(self, "class") else fromlist

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

    def __load__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        if self._py_object != None:
            return self._py_object
        else:
            super_dict = super().__dict__
            return dict(
                {key: val for key, val in super_dict.items() if not key.startswith("_")}
            )

    # def __dict__(self):
    #     super_dict = super().__dict__
    #     return dict({key: val for key, val in super_dict.items() if not key.startswith("_")})


class NodeDict(Node):
    def __init__(self, args, **kawrgs) -> None:
        assert type(args) == dict or type(args) == Bunch
        super().__init__(args, **kawrgs)

    def __load__(self, parent: Optional[Node] = None):

        for key, val in self.__dict__.items():
            val = load_node(val, parent=self)
            if isinstance(val, Node):
                val.__load__(self)
                setattr(self, key, val())
            elif isinstance(val, list):
                for i, item in enumerate(val):
                    item = load_node(item, parent=self)
                    if isinstance(item, Node):
                        item.__load__(self)
                        val[i] = item()

        self.load_dynamic_objects()

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.__dict__


class ObjectReference(Node):
    reference_key: str = ""
    _reference: Optional[Node] = None

    def __init__(self, args):
        super().__init__(args)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return Node._key_value_map[self.reference_key]


class MethodCall(ObjectReference):
    function_call: str = ""
    reference_key: Optional[str] = None
    params: Bunch = Bunch({})

    def __call__(self, parent: Optional[object] = None, *args, **kwargs):

        # first create DictNode of params
        dictNode = NodeDict(self.params)
        dictNode.__load__(self)

        # then call the function
        object = Node._key_value_map[self.reference_key]
        function = getattr(object, self.function_call)
        return function(*args, **dictNode())

    def __init__(self, args, parent: Optional[object] = None):
        super().__init__(args)


class MethodCall(ObjectReference):
    function: str = ""
    reference_key: Optional[str] = None
    params: Bunch = Bunch({})

    def __call__(self, parent: Optional[object] = None, *args, **kwargs):

        # first create DictNode of params
        dictNode = NodeDict(self.params)
        dictNode.__load__(self)

        # then call the function
        object = Node._key_value_map[self.reference_key]
        function = getattr(object, self.function_call)
        return function(*args, **dictNode())

    def __init__(self, args, parent: Optional[object] = None):
        super().__init__(args)


class Object(Node):
    module: str = ""
    class_name: str = ""
    params: Bunch = Bunch({})  # param is actualy a dictnode
    method_args: Optional[dict[str, MethodCall]] = None

    def __load__(self, parent: Optional[object] = None) -> object:

        if self._py_object != None:
            return self._py_object

        module = self.load_module()

        param_node = NodeDict(self.params)

        param_node.__load__(self)

        self._py_object = module(**param_node())

        self.post_object_creation()

        return self._py_object

    def __init__(self, args: Optional[Bunch] = None):
        super().__init__(args)


class Object(Node):
    module: str = ""
    class_name: str = ""
    params: Bunch = Bunch({})  # param is actualy a dictnode

    def __load__(self, parent: Optional[object] = None) -> object:

        if self._py_object != None:
            return self._py_object

        module = self.load_module()

        param_node = NodeDict(self.params)

        param_node.__load__(self)

        self._py_object = module(**param_node())

        self.post_object_creation()

        return self._py_object

    def __init__(self, args: Optional[Bunch], parent: Optional[object] = None):
        super().__init__(args, parent=parent)


# only accepted as method_args inside objects
class AnonMethodCall(Node):
    function: str = ""
    params: Bunch = Bunch({})

    def __load__(self, parent: Object = None) -> object:

        assert parent is not None, "AnonMethodCall must have a parent"
        setattr("object_key", parent.object_key)

    def __call__(self, *args, **kwargs):
        params_node = NodeDict(self.params)
        params_node.__load__(self)
        object = Node._key_value_map[self.object_key]

        return getattr(object, self.function)(*args, **(self.params_node() | kwargs))

    def __init__(self, args, parent: Optional[object] = None):
        super().__init__(args)


class AnnonymousObject(Node):
    def __init__(self, args: Optional[dict] = None) -> None:
        super().__init__(args)
        setattr(self, "", "")


node_types: list[Type] = [
    Object,
    MethodCall,
    ObjectReference,
    NodeDict,
    AnonMethodCall,
]
SyntaxNode = Union[Object, MethodCall, ObjectReference, AnonMethodCall, NodeDict]


def load_node(args, parent=None):
    if isinstance(args, dict):
        node: Optional[SyntaxNode] = None
        for node_type in node_types:
            if node_type.is_one(args):
                node = node_type(args, parent=parent)
                return node

    return args
