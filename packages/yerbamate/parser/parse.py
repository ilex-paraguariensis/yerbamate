from argparse import Namespace
import io
import re
from ..utils import utils
from ..utils.bunch import Bunch
# from .syntax import SyntaxNode, node_types
# from .syntax import Object, MethodCall
from typing import Optional, Union, Callable


class Parser:
    def __init__(self, root_module: str, base_module: str, map_key_values: dict):

        self.root_module = root_module
        self.base_module = base_module
        self.map_key_values = map_key_values
        self.object_dict = {}

    def parse_py_module_to_dict(
        self,
        definition: dict,
        object,
        generate_defauls: bool = False,
    ):

        # type annotation
        if "self" in definition and definition["self"] == True:
            return definition

        merged_params, error = utils.get_function_parameters(
            object, definition, generate_defauls
        )
        definition["params"] = merged_params.copy()

        return definition, error

    object_dict = {}

    # creates a module object from a dict and calls it with the params
    def parse_module_object(
        self,
        object: Bunch,
    ):
        module_class, params = self.parse_module_class_recursive(object)

        # ipdb.set_trace()
        if "self" in object.keys() and object["self"] == True:
            return module_class

        for key, value in params.items():
            if type(value) == dict and "object_key" in value and not "module" in value:
                # ipdb.set_trace()
                # find the object from the root
                if "function_call" in value:
                    function = value["function_call"]
                    function = getattr(self.object_dict[value["object_key"]], function)
                    py_object = function(value["object_key"])
                    # object = function(value[obj])
                else:
                    py_object = self.object_dict[value["object_key"]]
                params[key] = py_object

        if "function" in object.keys():
            function = getattr(module_class, object["function"])
            py_object = function(**params)
        elif "class" in object.keys():
            # ipdb.set_trace()
            py_object = module_class(**params)

        # save object in dict for later use
        if "object_key" in object and "module" in object.keys():
            self.object_dict[object["object_key"]] = py_object

        return py_object

        # function_name = object["function"] if "function" in object.keys() else "__init__"
        # function = getattr(module_class, function_name)
        return module_class(**params)

    

    # Loads a module from a dict, importing hiearchy is local -> base -> global
    def load_module(
        self, object: Bunch, base_module: str = None, root_module: str = None
    ):

        assert "module" in object
        assert "class" or "function" in object
        fromlist = [object["class"]] if "class" in object else [object["function"]]

        if root_module == None:
            root_module = self.root_module
        if base_module == None:
            base_module = self.base_module

        try:
            module = __import__(base_module + "." + object["module"], fromlist=fromlist)
        except ModuleNotFoundError:
            # now try shared imports
            try:
                module = __import__(
                    root_module + "." + object["module"], fromlist=fromlist
                )
            except ModuleNotFoundError:

                # lastly try global imports

                module = __import__(object["module"], fromlist=fromlist)

        if "class" in object:
            module = getattr(module, object["class"])

        return module

    def __parse_dict_object(
        self,
        object: dict,
    ):

        if type(object) == dict:

            if "module" and ("class" or "function") in object.keys():
                parsed_module = self.parse_module_object(object)
                return parsed_module

            # recursively check if the child object is a dict
            for key, value in object.items():
                object[key] = self.__parse_dict_object(value)

        if type(object) == list:
            result = [self.__parse_dict_object(item) for item in object]
            return result

        return object

    # Function to generate children of a object
    def __generate_children(
        self,
        object: Bunch,
    ):

        try:
            if "params" in object:
                params = object.get("params", {}).copy()
        except KeyError:
            params = {}
            object["params"] = {}
            # either empty params, no params or just a type?

        # recursively check if module has a object child
        # parse it and add it to the params

        new_params = {}
        # parse params
        for key, value in object["params"].items():
            if type(value) == dict or type(value) == list:
                new_params[key] = self.__parse_dict_object(value)

        params.update(new_params)

        # replace {regex} with values from map_key_values
        params = self.replace_key_values_no_depth(params)

        return params

    def replace_key_values_no_depth(self, object: Bunch):
        for key, value in object.items():

            if type(value) == str and re.search(r"{.*}", value):
                # get the key name
                key_name = re.search(r"{.*}", value).group(0)[1:-1]
                # replace the value
                object[key] = value.replace(
                    "{" + key_name + "}", self.map_key_values[key_name]
                )

        return object

    def is_object(self, object: Bunch):
        return "object_key" in object and "module" not in object.keys()

    # Function to parse a nested dict of python modules, classes and functions
    def parse_module_class_recursive(
        self,
        object: dict,
    ):
        if self.is_object(object):
            return self.object_dict[object["object_key"]]

        module = self.load_module(object)

        if "self" in object:
            return module, {}

        params = self.__generate_children(object)

        return module, params

    def generate_params_no_depth(
        self,
        object: Bunch,
        generate_defauls: bool = False,
    ):

        if "self" in object and object["self"] == True:
            return object, None

        if "module" not in object:
            return object, None

        module = self.load_module(object)

        callable = object["function"] if "function" in object else "__init__"

        object_definition, error = self.parse_py_module_to_dict(
            object, getattr(module, callable), generate_defauls
        )

        return object_definition, error

    def generate_params_recursively(
        self,
        object: Bunch,
        generate_default_params: bool = False,
    ):

        if "self" in object and object["self"] == True:
            return object, None

        assert "module" in object

        object, error = self.generate_params_no_depth(object, generate_default_params)
        errors = [error] if error else []

        if "params" in object:
            for key, value in object["params"].items():
                if type(value) == dict and (
                    "module" and ("class" or "function") in value.keys()
                ):
                    # ipdb.set_trace()
                    obj_def, error = self.generate_params_recursively(
                        value, generate_default_params
                    )
                    object["params"][key] = obj_def.copy()
                    errors += [error] if error else []

                if type(value) == list:

                    for index, item in enumerate(value):
                        if type(item) == dict and (
                            "module" and ("class" or "function") in item.keys()
                        ):

                            obj_def, error = self.generate_params_recursively(
                                item, generate_default_params
                            )
                            object["params"][key][index] = obj_def.copy()
                            errors += [error] if error else []

        return object, errors

    def generate_params(
        self,
        root: Bunch,
        generate_defauls: bool = False,
    ):

        # params = root.copy()

        errors = []
        root = root.copy()

        # # first generate the params for the root
        # if "module" in root:
        #     root, error = generate_params_no_depth(root, base_module, root_module)
        #     errors += [error] if error else []

        # then generate the params for the children
        for key, value in root.items():
            if type(value) == dict and (
                "module" and ("class" or "function") in value.keys()
            ):
                gen_def, err = self.generate_params_recursively(
                    root[key], generate_defauls
                )
                root[key] = gen_def.copy()

                errors += err

        # remove None from erros
        errors = [error for error in errors if error]

        return root, errors

    # entrypoint
    def load_python_object(
        self,
        object: Bunch,
    ):
        if "module" in object:
            model_class, obj_params = self.parse_module_class_recursive(object)
            o = model_class(**obj_params)
            if "object_key" in object:
                self.object_dict[object["object_key"]] = o

            return o

        elif "object_key" in object:
            return self.object_dict[object["object_key"]]

        result = {}

        for key, value in object.items():
            if type(value) == dict:
                result[key] = self.load_python_object(value)
            elif type(value) == list:
                result[key] = [self.load_python_object(item) for item in value]
            else:
                result[key] = value

        # replace {regex} with values from map_key_values
        result = self.replace_key_values_no_depth(result)

        return result

    def load_method_args(self, object: Bunch, method: str):

        assert "method_args" in object, "method_args not in object"

        if type(object["method_args"]) == dict:
            return self.load_python_object(object["method_args"])

        for i in range(len(object["method_args"])):
            if method in object["method_args"][i].keys():
                return self.load_python_object(object["method_args"][i])

        raise Exception("method not found in method_args")

    def call_method(self, object: Bunch, method: str, *args, **kwargs):

        assert (
            "object_key" in object
        ), "object_key not in object, only objets with key are callable"

        params = self.load_method_args(object, method)
        params = params[method]

        object = self.object_dict[object["object_key"]]

        # ipdb.set_trace()

        return getattr(object, method)(*args, **params, **kwargs)


if __name__ == "__main__":
    pass
