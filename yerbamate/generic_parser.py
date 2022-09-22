#!/usr/bin/env python3

import io
import re
from .bunch import Bunch
import ipdb
import json
from .node import SyntaxNode, node_types
from .node import Object, MethodCall
from typing import Optional, Union, Callable

SimpleType = Union[str, int, float, bool, None]


def parse_nodes_recursive(
    args: Union[SyntaxNode, SimpleType],
    references: dict[
        str, list[SyntaxNode]
    ],  # dict of references, will be filled up during parsing
    objects: dict[
        str, SyntaxNode
    ],  # dict of nodes of type Object, will be filled up during parsing
    on_references_assigned: list[Callable],
    parent: Union[SyntaxNode, dict]
    # list of callbacks to be called when all references are assigned
):
    if isinstance(args, dict):
        node: Optional[SyntaxNode] = None
        for node_type in node_types:
            if node_type.is_one(args):
                node = node_type(args)
                objects[node.object_key] = node
                if hasattr(node_type, "reference_key"):
                    if node.reference_key == None:
                        node.reference_key = parent.object_key
                    if not node.reference_key in references:
                        references[node.reference_key] = []
                    references[node.reference_key].append(node)
        if node is None:
            raise SyntaxError(f"Invalid Node:\n{json.dumps(args, indent=4)}")
        else:
            for key, val in args.items():
                if key == "params":
                    for subkey, subval in val.items():
                        try:
                            node.__dict__[key][subkey] = parse_nodes_recursive(
                                subval,
                                references,
                                objects,
                                on_references_assigned,
                                node,
                            )
                        except:
                            ipdb.set_trace()
                elif isinstance(val, list):
                    node.__dict__[key] = []
                    for item in val:
                        node.__dict__[key].append(
                            parse_nodes_recursive(
                                item,
                                references,
                                objects,
                                on_references_assigned,
                                node,
                            )
                        )
        return node
    else:
        return args


def parse_nodes(args: Bunch):
    references = {}
    objects = {}
    on_references_assigned = []
    result = {}
    # ipdb.set_trace()

    for key, value in args.items():
        result[key] = parse_nodes_recursive(
            value, references, objects, on_references_assigned, result
        )
    # the entire tree is parsed, now we can assign references
    dictionary = {key: val._json() for key, val in objects.items()}
    for key, val in objects.items():
        if key in references:
            for reference in references[key]:
                reference._reference = val
    # ipdb.set_trace()
    # print(json.dumps(dictionary, indent=4))
    # ipdb.set_trace()
    return result


def test():
    with open("sample_params/test.json") as f:
        args = Bunch(json.load(f))
    parse_nodes(args)


if __name__ == "__main__":
    test()
