"""
## Cli Parser

Mate's cli parser is a simple parser that parses the command line arguments and calls the appropriate method on the Mate class.

Notice that for boolean arguments, you can use either false or False, true or True. And for None you can use either null or None.

**Example**

```
mate init my_project venv=false
```

"""
from .utils import print_markdown, remove_indent
from .mate import Mate
import inspect
from typing import Optional, Callable, Sized
import ipdb
import os
import sys


def __parse_signature(class_name, method_name: str):
    return tuple(
        val
        for (name, val) in inspect.signature(
            getattr(class_name, method_name)
        ).parameters.items()
        if name != "self"
    )


def __get_methods_with_arguments(class_name):
    return {
        k: __parse_signature(class_name, k)
        for k in class_name.__dict__.keys()
        if not k.startswith("_")
    }


def method_to_md(method_name, member: Optional[Callable] = None):
    if member is None:
        member = getattr(MateCLI, method_name)
    assert member is not None
    params = inspect.signature(member).parameters.values()
    inline_params = " ".join(
        [
            f"<{param.name}{('=' + str(param.default)) if (param.default != inspect._empty) else ''}>"
            for param in params
            if param.name != "self"
        ]
    )
    param_descriptions = {
        line[1].split(" ")[1]: ":".join(line[2:])
        for line in [l.strip().split(":") for l in str(member.__doc__).split("\n")]
        if len(line) > 1 and line[1].startswith("param")
    }

    raw_list_params = [
        f"- {param.name} : `{param.annotation.__name__}` : {param_descriptions.get(param.name, '')}"
        + (f"={param.default}" if param.default != inspect._empty else "")
        for param in params
        if param.name != "self"
    ]
    list_params = "\n".join(raw_list_params)
    method_description = "\n".join(
        [
            line
            for line in str(member.__doc__).split("\n")
            if not line.strip().startswith(":param")
        ]
    )

    code = remove_indent(
        f"""
    ```
      ❯ mate {method_name} {inline_params}
    ```
    """
    ).strip()
    doc = remove_indent(
        f"""
{code}

**Params**

{list_params.strip()}

{remove_indent(method_description)}

---
"""
    )

    return remove_indent(doc)


def generate_help_md() -> str:

    doc = remove_indent(str(Mate.__doc__)) + "\n --- \n"
    current_docstring = str(sys.modules[__name__].__doc__)
    doc += current_docstring + "\n --- \n"
    members = [
        (k, v)
        for (k, v) in inspect.getmembers(Mate, predicate=inspect.isfunction)
        if not k.startswith("_")
    ]
    for name, val in members:
        doc += method_to_md(name, val)
    return doc


class MateHelp:
    def __init__(self):
        self.help_options = (
            "init",
            "install",
            "train",
            "auto",
            "export",
            "clone",
            "test",
        )
        self.help_comments = (
            "Initialize a new project",
            "Install dependencies",
            "Train a model",
            "Various commands to help with the development proces",
            "Export dependencies",
            "Clones internal modules",
            "Test a model",
        )

        self._full_docs, self._methods = self.get_full_docs(Mate)

        # save full docs to file
        # with open("docs.md", "w") as f:
        #     f.write(self._full_docs)

    def get_index(self):
        nl = "\n"
        # return self._full_docs

        helps = [
            f"`{option}` : {comment}"
            for option, comment in zip(self.help_options, self.help_comments)
        ]
        return remove_indent(
            f"""
        # Help Index

        Mate, your friendly ML project manager.
        
        Type `mate help <option>` to get more information about a topic.

        Available options are:

        {'- ' + (nl + ' - ').join(helps)}
        """
        )

    def get_full_docs(self, class_value):
        header = remove_indent(class_value.__doc__) + "\n\n --- \n"
        # gets the docstring of the methods and the variables with inspect
        def get_method_doc(method_name, method):
            doc = remove_indent(method.__doc__)
            signature = inspect.signature(method)
            args = list(signature.parameters.values())
            is_static = args[0].name != "self"
            args = [arg for arg in args if arg.name != "self"]
            annotations = ", ".join([str(a) for a in list(args)])
            header = f"### `mate` {method_name}\n"
            return header + doc + "\n --- \n"

        # methods = [
        #     get_method_doc(method_name, method)
        #     for method_name, method in inspect.getmembers(
        #         class_value, inspect.isfunction
        #     )
        #     if not method_name.startswith("_") and method.__doc__ is not None
        # ]

        method_dict = {
            method_name: get_method_doc(method_name=method_name, method=method)
            for method_name, method in inspect.getmembers(
                class_value, inspect.isfunction
            )
            if not method_name.startswith("_") and method.__doc__ is not None
        }

        nl = "\n"
        return (
            f"{header}\n\n{remove_indent(nl.join(method_dict.values()))}",
            method_dict,
        )

    def print_help(self, what: str = "") -> None:

        if what in self.help_options:
            # ipdb.set_trace()
            print_markdown(self._methods[what])
        else:
            print_markdown(self.get_index())
        # if what == "cli":
        #     print(generate_help_md())
        #     print_markdown(generate_help_md())
        # elif what == "mate":
        #     test = self.get_full_docs(Mate)
        #     print_markdown(test)
        # # elif what == "config":
        # #     print_markdown(MateConfig.__doc__)
        # # elif what == "project":
        # #     print_markdown(MateProject.__doc__)
        # # elif what == "experiment":
        # #     print_markdown(Experiment.__doc__)
        # else:
        #     # print_markdown(generate_help_md())
        #     print_markdown(self.get_index())

    def get_help_md(self, what: str = "cli") -> str:
        if what == "cli":
            return generate_help_md()
        elif what == "mate":
            return str(self.get_full_docs(Mate))
        # elif what == "config":
        #     return str(MateConfig.__doc__)
        # elif what == "project":
        #     return str(MateProject.__doc__)
        # elif what == "experiment":
        #     return str(Experiment.__doc__)
        else:
            return generate_help_md()

    def get_all_help_md(self) -> dict[str, str]:
        return {key: self.get_help_md(key) for key in self.help_options}


def collect_args(args: list[str], annotations: tuple[Callable]) -> tuple[list, dict]:
    # collects the arguments into a list and a dictionary
    # the list contains the positional arguments
    # the dictionary contains the keyword arguments
    # the arguments are split by the "=" sign
    # if there is no "=" sign, the argument is considered a positional argument
    # it also checks that there are no positional arguments after keyword arguments
    kwargs = {}
    positional_args = []
    positional_args_started = False

    def good_guess_type(arg: str):
        types = [int, float, str]
        if arg.lower() in ("none", "null"):
            return None
        elif arg.lower() == "true":
            return True
        elif arg.lower() == "false":
            return False
        for t in types:
            try:
                return t(arg)
            except ValueError:
                pass

    def boolean_type(arg: str):
        if arg.lower() == "true":
            return True
        elif arg.lower() == "false":
            return False
        else:
            raise ValueError("Not a boolean")

    if len(annotations) < len(args):
        annotations = annotations + (good_guess_type,) * (len(args) - len(annotations))

    for i, (arg, annotation) in enumerate(zip(args, annotations)):
        if annotation == bool:
            annotation = boolean_type
        elif annotation == inspect._empty:
            annotation = good_guess_type
        elif hasattr(annotation, "__args__"):
            annotation = annotation.__args__
        if "=" in arg:
            key, value = arg.split("=")
            kwargs[key] = annotation(value)
            positional_args_started = True
        else:
            if isinstance(annotation, tuple):
                annotation = annotation[0]
            positional_args.append(annotation(arg))
            if positional_args_started:
                raise ValueError(
                    f"positional argument {arg} after keyword argument {args[i-1]}"
                )

    return positional_args, kwargs


def main():
    methods = __get_methods_with_arguments(Mate)
    args = sys.argv[1:]
    raw_method_args = args[1:]
    help_args = ("help", "--help", "-h")
    actions = tuple(method.replace("_", "-") for method in methods) + help_args
    help = MateHelp()
    # ipdb.set_trace()
    if len(args) == 0 or args[0] in help_args:
        if len(args) > 1:
            help.print_help(args[1])
        else:
            help.print_help()
    else:
        # if args[0] not in actions:
        #     help.print_help()
        action = args[0]
        if len(args) > 1 and args[1] in ("--help", "-h"):
            md = method_to_md(action)
            print_markdown(md)

        elif action not in methods:
            try:
                mate = Mate()
                mate.train(*args[1:])
            except Exception as e:
                print(e)
                help.print_help()

        else:
            annotations = tuple(
                param.annotation
                for param in methods[action]
                if (param.kind != inspect.Parameter.VAR_KEYWORD)
                and (param.kind != inspect.Parameter.VAR_POSITIONAL)
            )

            pos_args, kwargs = collect_args(raw_method_args, annotations)
            if action == "init":
                Mate.init(*pos_args, **kwargs)
            else:
                mate = Mate()
                if hasattr(mate, action):
                    getattr(mate, action)(*pos_args, **kwargs)
                elif len(pos_args) == 2:
                        mate.train(*pos_args)
                else:
                    mate.run_module(sys.argv[1], sys.argv[2], sys.argv[3])
