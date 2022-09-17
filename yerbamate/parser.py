# A parser for mate formatted nested dict values of python modules, classes and functions


from argparse import Namespace
import io
import re
from yerbamate import utils
from yerbamate import bunch
from yerbamate.bunch import Bunch
import ipdb


def parse_module_object(
    object: Bunch,
    base_module: str = "",
    root_module: str = "",
    map_key_values: dict = {},
):

    module_class, params = parse_module_class_recursive(
        object, base_module, root_module, map_key_values
    )

    if "function" in object:
        function = getattr(module_class, object["function"])
        return function(**params)

    if "self" in object:
        return module_class

    return module_class(**params)


# Function to parse a nested dict of python modules, classes and functions


def parse_module_class_recursive(
    object: Bunch,
    base_module: str = "",
    root_module: str = "",
    map_key_values: dict = {},
    generate_params: bool = True,
):

    # object should have a module and a class and params in dict keys
    assert "module" in object
    assert "class" or "function" in object
    # first try local imports
    fromlist = [object["class"]] if "class" in object else [object["function"]]
    try:
        module = __import__(base_module + "." + object["module"], fromlist=fromlist)
    except ModuleNotFoundError:
        # now try shared imports
        try:
            module = __import__(root_module + "." + object["module"], fromlist=fromlist)
        except ModuleNotFoundError:

            # lastly try global imports
            module = __import__(object["module"], fromlist=fromlist)

    if "class" in object:
        module = getattr(module, object["class"])

    try:
        params = object["params"]
    except KeyError:
        params = {}
        object["params"] = {}
        # either empty params, no params or just a type?

    # recursively check if module has a object child
    # parse it and add it to the params

    new_params = {}
    # parse params
    for key, value in object["params"].items():
        if type(value) == dict and "module" in value.keys():
            new_params[key] = parse_module_object(
                value, base_module, root_module, map_key_values
            )
        if type(value) == list:
            new_params[key] = []
            for item in value:
                if type(item) == dict and "module" in item.keys():
                    new_params[key].append(
                        parse_module_object(
                            item, base_module, root_module, map_key_values
                        )
                    )
                else:
                    new_params[key].append(item)

    params.update(new_params)

    # TODO generalizable way to do this
    # replace {regex} with values from map_key_values
    for key, value in params.items():

        # regex for {anystring}
        if type(value) == str and re.search(r"{.*}", value):
            # get the key name
            key_name = re.search(r"{.*}", value).group(0)[1:-1]
            # replace the value
            params[key] = value.replace("{" + key_name + "}", map_key_values[key_name])

    # inspect the signature of the function
    if "class" or "function" in object:

        function = object["function"] if "function" in object else "__init__"
        callable = getattr(module, function)
        default_params = utils.get_function_parameters(callable)
        # ipdb.set_trace()
        # combine default params with params

        # for key, value in default_params.items():
        #     if key not in params.keys() and value != None:
        #         # params[key] = value
        #         object["params"][key] = value
        #         params[key] = value

        # if key in default_params and key not in params:
        #     params[key] = default_params[key]
        # if key not in default_params and key not in params:
        #     raise Exception(
        #         f"Parameter {key} not found in function {function} of module {module}")

        return module, params

    return module, params


# maybe we need model_name and experiment for populating the params
def load_python_object(
    model_name: str,
    experiment: str,
    object: Bunch,
    root: Bunch,
    base_module: str,
    root_module: str,
    map_key_values: dict = {},
):

    model_class, obj_params = parse_module_class_recursive(
        object,
        base_module=base_module,
        root_module=root_module,
        map_key_values=map_key_values,
    )

    if (
        root != None
        and "params" in object.params
        and "module" in object.params.params
        and object.params.params.module == "argparse"
        and object.params.params.self == True
    ):
        obj_params["params"] = Namespace(**root.clone())

    if "self" in object:
        return model_class

    return model_class(**obj_params)


if __name__ == "__main__":
    pass
