from typing import Callable
import inspect
import ipdb


def parse_default_param(param):

    # if param is object:
    #     ipdb.set_trace()

    # if param is a class, return the class name
    if inspect.isclass(param):
        return {
            "class_type": param.__name__,
            "module": param.__module__,
        }

    if param is list:
        return [parse_default_param(p) for p in param]

    return param


def parse_type_annotation(annotation):
    if annotation is None:
        return None

    # ipdb.set_trace()
    # if inspect.isclass(annotation):
    #     return annotation.__name__

    return {
        "class": annotation.__name__,
        "module": annotation.__module__,
    }


def get_function_args(
    function: Callable,
    args={},
    generate_defaults: bool = True,
    generate_none: bool = False,
):

    params = args.to_dict() if hasattr(args, "to_dict") else args
    default = {}
    errors = []

    for param_name, param in inspect.signature(function).parameters.items():
        # only add parameters that are not self or exist in the params

        if param_name in params or param_name == "self":
            continue

        # only allow named parameters and not *args or **kwargs
        if param.kind != param.POSITIONAL_OR_KEYWORD:
            continue

        if param.default is not param.empty:
            # ignore None values
            if param.default != None and generate_defaults:
                default[param_name] = parse_default_param(param.default)

                # check if default is type class, or object

            elif generate_none:
                default[param_name] = None

        elif param.annotation is not param.empty:
            default[param_name] = parse_type_annotation(param.annotation)
            error = f"Missing parameter {param_name}.  Hint: {param.annotation}"
            errors.append(error)
        else:
            default[param_name] = {
                "type": "unknown",
                "description": "Unknown type, please add a type annotation or sample value",
            }
            error = f"Missing parameter {param_name}. Hint: Add a default value or type annotation"
            errors.append(error)

        #

    params.update(default)

    return params, errors
