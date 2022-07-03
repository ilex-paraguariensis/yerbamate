from argparse import ArgumentParser
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


def main():
    parser = ArgumentParser()
    methods = get_methods_with_arguments(Mate)
    max_len = max(len(args) for args in methods)
    parser.add_argument(
        "action",
        choices=tuple(method.replace("_", "-") for method, _ in methods),
        type=str,
        nargs="?",
    )
    for i in range(max_len):
        parser.add_argument(f"arg_{i}", type=str, nargs="?")
    args = parser.parse_args()
    args.action = args.action.replace("-", "_")
    mate = Mate()
    method_args_types = tuple(
        tuple(param.annotation for param in params)
        for method, params in methods
        if method == args.action
    )[0]
    method_args_defaults = tuple(
        tuple(param.default for param in params)
        for method, params in methods
        if method == args.action
    )[0]

    raw_method_args = tuple(
        args.__dict__[f"arg_{i}"] for i in range(len(method_args_types))
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
    ipdb.set_trace()
    getattr(mate, args.action)(*method_args)
