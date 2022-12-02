from .utils.bunch import Bunch
from .mate import Mate
import inspect
import ipdb
import sys
from pydoc import locate
from typing import Any


def parse_signature(class_name, method_name: str):
    return tuple(
        val
        for (name, val) in inspect.signature(
            getattr(class_name, method_name)
        ).parameters.items()
        if name != "self"
    )


def get_methods_with_arguments(class_name):
    return {
        k: parse_signature(class_name, k)
        for k in class_name.__dict__.keys()
        if not k.startswith("_")
    }


def prettify_method(method_name, annotation, in_depth: bool = False):
    def cleanup(ann):
        return str(ann).replace("<class ", "").replace(">", "").replace("'", "")

    def pretty(m):
        return ",\n\t".join(
            [
                f"{m.name}: {cleanup(m.annotation)}"
                + (f"={m.default}" if m.default != inspect._empty else "")
                for m in annotation
            ]
        )

    source_code = inspect.getsource(getattr(Mate, method_name))
    description = (
        source_code.split('"""')[1] if '"""' in source_code and in_depth else ""
    )
    return f" {method_name}\n\t{pretty(annotation)}\n" + description


def print_help(methods):
    for method_name, annotation in methods.items():
        print(prettify_method(method_name, annotation))


def convert_str_to_data(input):
    try:
        return int(input)
    except ValueError:
        try:
            return float(input)
        except ValueError:
            if input in ["True", "true"]:
                return True
            elif input in ["False", "false"]:
                return False

    return input


def parse_run_params(args: list):
    params = {}
    for arg in args:
        key, value = arg.split("=")
        params[key[2:]] = convert_str_to_data(value)
    return params


def main():
    methods = get_methods_with_arguments(Mate)
    args = sys.argv[1:]
    raw_method_args = args[1:]
    actions = tuple(method.replace("_", "-") for method in methods) + (
        "--help",
        "-h",
    )
    if len(args) == 0 or not args[0] in actions or args[0] in ("--help", "-h"):
        print_help(methods)
    else:
        assert args[0] in actions, print_help(methods)
        action = args[0].replace("-", "_")
        if len(args) > 1 and args[1] in ("--help", "-h"):
            print(prettify_method(action, methods[args[0]], in_depth=True))
        else:
            method_args_types = tuple(param.annotation for param in methods[action])
            method_args_defaults = tuple(
                tuple(param.default for param in methods[action])
            )
            method_args = tuple(
                (
                    method_type(raw_method_arg)
                    if (raw_method_arg is not None)
                    else method_default
                )
                for (method_type, method_default, raw_method_arg) in zip(
                    method_args_types, method_args_defaults, raw_method_args
                )
            )
            if action == "init":
                Mate.init(*method_args)
            else:
                mate = Mate()
                method_args_len = len(method_args)
                hparams_len = len(raw_method_args) - method_args_len
                if hparams_len > 0:
                    run_params = parse_run_params(args[method_args_len + 1 :])
                    mate.run_params = run_params
                getattr(mate, action)(*method_args)
