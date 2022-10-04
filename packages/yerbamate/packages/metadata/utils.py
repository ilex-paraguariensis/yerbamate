from typing import Callable
import inspect
import ipdb


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
                default[param_name] = param.default
            elif generate_none:
                default[param_name] = None

        elif param.annotation is not param.empty:
            default[param_name] = f"Fix me! {param.annotation}"
            error = f"Missing parameter {param_name} for {object['module']}\nHint: {param.annotation}"
            errors.append(error)
        else:
            default[param_name] = "Fix me!"
            error = f"Missing parameter {param_name} for {object['module']}\nHint: Add a default value or type annotation"
            errors.append(error)

    params.update(default)

    return params, errors
