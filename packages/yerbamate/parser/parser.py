# A parser for mate formatted nested dict values of python modules, classes and functions


from argparse import Namespace
import io
import re
from typing import Callable
from ..utils import utils
from ..utils.bunch import Bunch
import ipdb


def parse_py_module_to_dict(
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
    root: Bunch,
    object: Bunch,
    base_module: str = "",
    root_module: str = "",
    map_key_values: dict = {},
):

    module_class, params = parse_module_class_recursive(
        root, object, base_module, root_module, map_key_values
    )

    # ipdb.set_trace()
    if "self" in object.keys() and object["self"] == True:
        return module_class

    for key, value in params.items():
        if type(value) == dict and "object_key" in value and not "module" in value:
            # ipdb.set_trace()
            # find the object from the root
            if "function_call" in value:
                function = value["function_call"]
                function = getattr(object_dict[value["object_key"]], function)
                py_object = function(value["object_key"])
                # object = function(value[obj])
            else:
                py_object = object_dict[value["object_key"]]
            params[key] = py_object

    if "function" in object.keys():
        function = getattr(module_class, object["function"])
        py_object = function(**params)
    elif "class" in object.keys():
        # ipdb.set_trace()
        py_object = module_class(**params)

    # save object in dict for later use
    if "object_key" in object and "module" in object.keys():
        # ipdb.set_trace()
        object_dict[object["object_key"]] = py_object

    return py_object

    # function_name = object["function"] if "function" in object.keys() else "__init__"
    # function = getattr(module_class, function_name)
    return module_class(**params)


# Loads a module from a dict, importing hiearchy is local -> base -> global
def load_module(object: Bunch, base_module: str, root_module: str):

    assert "module" in object
    assert "class" or "function" in object
    fromlist = [object["class"]] if "class" in object else [object["function"]]
    try:
        module = __import__(base_module + "." + object["module"], fromlist=fromlist)
    except ModuleNotFoundError:
        # now try shared imports
        try:
            module = __import__(root_module + "." + object["module"], fromlist=fromlist)
        except ModuleNotFoundError:

            # lastly try global imports
            try:
                module = __import__(object["module"], fromlist=fromlist)
            except ModuleNotFoundError:
                return object

    if "class" in object:
        module = getattr(module, object["class"])

    return module


def __parse_dict_object(
    root: Bunch,
    object: dict,
    base_module: str,
    root_module: str,
    map_key_values: dict,
):

    if type(object) == dict:

        if "module" and ("class" or "function") in object.keys():
            parsed_module = parse_module_object(
                root, object, base_module, root_module, map_key_values
            )
            return parsed_module

        # check if the object is a dict with a function
        for key, value in object.items():
            object[key] = __parse_dict_object(
                root, value, base_module, root_module, map_key_values
            )
            # if type(value) == dict and (
            #     "module" and ("class" or "function") in value.keys()
            # ):
            #     object[key] = parse_module_object(
            #         root, value, base_module, root_module, map_key_values
            #     )

            # elif type(value) == dict:
            #     for _key, _value in value.items():
            #         if type(_value) == dict and (
            #             "module" and ("class" or "function") in _value.keys()
            #         ):
            #             object[key][_key] = parse_module_object(
            #                 root, _value, base_module, root_module, map_key_values
            #             )

            # if type(value) == list:
            #     for index, item in enumerate(value):
            #         if type(item) == dict and (
            #             "module" and ("class" or "function") in item.keys()
            #         ):
            #             object[key][index] = parse_module_object(
            #                 root, item, base_module, root_module, map_key_values
            #             )

    if type(object) == list:
        result = [
            __parse_dict_object(root, item, base_module, root_module, map_key_values)
            for item in object
        ]
        return result

    return object


# Function to generate children of a object
def __generate_children(
    root: Bunch,
    object: Bunch,
    base_module: str,
    root_module: str,
    map_key_values: dict = {},
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
            new_params[key] = __parse_dict_object(
                root, value, base_module, root_module, map_key_values
            )

    params.update(new_params)

    # replace {regex} with values from map_key_values
    for key, value in params.items():

        # regex for {anystring}
        if type(value) == str and re.search(r"{.*}", value):
            # get the key name
            key_name = re.search(r"{.*}", value).group(0)[1:-1]
            # replace the value
            params[key] = value.replace("{" + key_name + "}", map_key_values[key_name])

    return params


# Function to parse a nested dict of python modules, classes and functions
def parse_module_class_recursive(
    root: Bunch,
    object: dict,
    base_module: str = "",
    root_module: str = "",
    map_key_values: dict = {},
):

    module = load_module(object, base_module, root_module)

    if "self" in object:
        return module, {}

    params = __generate_children(root, object, base_module, root_module, map_key_values)

    return module, params


def generate_params_no_depth(
    object: Bunch,
    base_module: str,
    root_module: str,
    generate_defauls: bool = False,
):

    if "self" in object and object["self"] == True:
        return object, None

    if "module" not in object:
        return object, None

    module = load_module(object, base_module, root_module)

    callable = object["function"] if "function" in object else "__init__"

    object_definition, error = parse_py_module_to_dict(
        object, getattr(module, callable), generate_defauls
    )

    return object_definition, error


def generate_params_recursively(
    object: Bunch,
    base_module: str,
    root_module: str,
    generate_default_params: bool = False,
):

    if "self" in object and object["self"] == True:
        return object, None

    assert "module" in object

    object, error = generate_params_no_depth(
        object, base_module, root_module, generate_default_params
    )
    errors = [error] if error else []

    if "params" in object:
        for key, value in object["params"].items():
            if type(value) == dict and (
                "module" and ("class" or "function") in value.keys()
            ):
                # ipdb.set_trace()
                obj_def, error = generate_params_recursively(
                    value, base_module, root_module, generate_default_params
                )
                object["params"][key] = obj_def.copy()
                errors += [error] if error else []

            if type(value) == list:

                for index, item in enumerate(value):
                    if type(item) == dict and (
                        "module" and ("class" or "function") in item.keys()
                    ):

                        obj_def, error = generate_params_recursively(
                            item, base_module, root_module, generate_default_params
                        )
                        object["params"][key][index] = obj_def.copy()
                        errors += [error] if error else []

    return object, errors


def generate_params(
    root: Bunch,
    base_module: str,
    root_module: str,
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
            gen_def, err = generate_params_recursively(
                root[key], base_module, root_module, generate_defauls
            )
            root[key] = gen_def.copy()

            errors += err

    # remove None from erros
    errors = [error for error in errors if error]

    return root, errors


def load_python_object(
    object: Bunch,
    root: Bunch,
    base_module: str,
    root_module: str,
    map_key_values: dict = {},
):

    # _, _ = generate_full_params(root, base_module, root_module)

    if "module" in object:
        model_class, obj_params = parse_module_class_recursive(
            root,
            object,
            base_module=base_module,
            root_module=root_module,
            map_key_values=map_key_values,
        )

        return model_class(**obj_params)

    result = {}

    for key, value in object.items():
        if type(value) == dict and (
            "module" and ("class" or "function") in value.keys()
        ):
            result[key] = load_python_object(
                value, root, base_module, root_module, map_key_values
            )
        elif type(value) == list:
            result[key] = [
                load_python_object(item, root, base_module, root_module, map_key_values)
                for item in value
            ]
        elif type(value) == dict:
            result[key] = load_python_object(
                value, root, base_module, root_module, map_key_values
            )
        else:
            result[key] = value

    return result


if __name__ == "__main__":
    pass
