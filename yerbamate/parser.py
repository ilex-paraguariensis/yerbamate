# A parser for mate formatted nested dict values of python modules, classes and functions


import re
from yerbamate.bunch import Bunch
import ipdb




def parse_module_object(
    object: Bunch, base_module: str = "", root_module: str = "", map_key_values: dict = {}
):

    module_class, params = parse_module_class_recursive(
        object, base_module, root_module, map_key_values)

    if "function" in object:
        function = getattr(module_class, object["function"])
        return function(**params)

    return module_class(**params)

# Function to parse a nested dict of python modules, classes and functions


def parse_module_class_recursive(
    object: Bunch, base_module: str = "", root_module: str = "", map_key_values: dict = {}, generate_params: bool = True


):

    # object should have a module and a class and params in dict keys
    assert "module", "class" in object

    # first try local imports
    try:
        module = __import__(
            base_module+"."+object["module"], fromlist=[object["class"]])
    except ModuleNotFoundError:
        # now try shared imports
        try:
            module = __import__(
                root_module+"."+object["module"], fromlist=[object["class"]])
        except ModuleNotFoundError:

            # lastly try global imports
            module = __import__(
                object["module"], fromlist=[object["class"]])

    module_class = getattr(module, object["class"])
    params = object["params"]
    new_params = {}
    # parse params
    for key, value in object["params"].items():
        if type(value) == dict and "module" in value.keys():
            new_params[key] = parse_module_object(
                value, base_module, root_module, map_key_values)
        if type(value) == list:
            new_params[key] = []
            for item in value:
                if type(item) == dict and "module" in item.keys():
                    new_params[key].append(
                        parse_module_object(
                            item, base_module, root_module, map_key_values))
                else:
                    new_params[key].append(item)

    params.update(new_params)

    # TODO generalizable way to do this
    # replace {save_dir} values to sef.save_path
    for key, value in params.items():

        # regex for {anystring}
        if type(value) == str and re.search(r"{.*}", value):
            # get the key name
            key_name = re.search(r"{.*}", value).group(0)[1:-1]
            # replace the value
            params[key] = value.replace(
                "{"+key_name+"}", map_key_values[key_name])

        # if type(value) == str and "{save_dir}" in value:
        #     params[key] = value.replace("{save_dir}", self.save_path)

    return module_class, params


if __name__ == "__main__":
    pass
