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
    return tuple(
        (k, parse_signature(class_name, k))
        for k in class_name.__dict__.keys()
        if not k.startswith("_")
    )


def prettify_method(method, in_depth: bool = False):
    def cleanup(ann):
        return (
            str(ann).replace("<class ", "").replace(">", "").replace("'", "")
        )

    def pretty(m):
        return ",\n\t".join(
            [
                f"{m.name}: {cleanup(m.annotation)}"
                + (f"={m.default}" if m.default != inspect._empty else "")
                for m in method[1]
            ]
        )

    source_code = inspect.getsource(getattr(Mate, method[0]))
    description = (
        source_code.split('"""')[1]
        if '"""' in source_code and in_depth
        else ""
    )
    return f" {method[0]}\n\t{pretty(method[1])}\n" + description


def print_help(methods):
    for method in methods:
        print(prettify_method(method) + "\n")


def main():
    methods = get_methods_with_arguments(Mate)
    max_len = max(len(args[1]) for args in methods)
    """
    parser.add_argument(
        "action",
        choices=tuple(method.replace("_", "-") for method, _ in methods)
        + ("help",),
        type=str,
        nargs="?",
    )
    """
    args = sys.argv[1:]
    actions = tuple(method.replace("_", "-") for method, _ in methods) + (
        "--help",
        "-h",
    )

    if len(args) == 0 or not args[0] in actions or args[0] in ("--help", "-h"):
        print_help(methods)
    elif len(args) > 1 and args[1] in ("--help", "-h"):
        print(
            prettify_method(
                [m for m in methods if m[0] == args[0]][0], in_depth=True
            )
        )
    # args.action = args.action.replace("-", "_")
    else:
        action = args[0]
        mate = Mate()
        method_args_types = tuple(
            tuple(param.annotation for param in params)
            for method, params in methods
            if method == action
        )[0]
        method_args_defaults = tuple(
            tuple(param.default for param in params)
            for method, params in methods
            if method == action
        )[0]
        raw_method_args = args[1:]
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
        getattr(mate, action)(*method_args)
