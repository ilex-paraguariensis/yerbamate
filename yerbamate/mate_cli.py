from argparse import ArgumentParser
from .mate import Mate
import inspect
import ipdb
import sys
from pydoc import locate
from typing import Any


def parse_signature(class_name, method_name: str):
    return tuple(
        (
            name,
            locate(str(val).split(":")[1].strip(" "))
            if ":" in str(val)
            else Any,
        )
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
        choices=tuple(method[0].replace("_", "-") for method in methods),
        type=str,
        nargs="?",
    )
    for i in range(max_len):
        parser.add_argument(f"arg_{i}", type=str, nargs="?")
    args = parser.parse_args()
    args.action = args.action.replace("-", "_")
    mate = Mate()
    method_args_types = tuple(
        tuple(m[1] for m in ma[1]) for ma in methods if ma[0] == args.action
    )[0]
    method_args = tuple(
        method_type(args.__dict__[f"arg_{i}"])
        for i, method_type in enumerate(method_args_types)
    )
    getattr(mate, args.action)(*method_args)
