import os

import sys, inspect

from ..package import Package
import ipdb

from bombilla.utils import get_function_args


class ModuleMetadataGenerator:
    def __init__(
        self,
        root_module: str,
        type_module: str,
        local_module: str,
        package_info: Package = None,
    ):

        self.root_module = root_module
        self.type_module = type_module
        self.local_module = local_module
        self.package_info = package_info

        self.module_path = os.path.join(
            self.root_module, self.type_module, self.local_module
        )
        # self.module = self.__get_local_module()
        self.module_files = os.listdir(self.module_path)

    def generate(self):

        self.module = self.__get_local_module()
        # ipdb.set_trace()
        classes = self.__find_classes(self.module)

        meta = [self.generate_class_metadata(klass) for klass in classes]

        functions = self.__find_functions(self.module)

        fun_meta = [self.generate_function_metadata(function) for function in functions]

        return {
            "classes": meta,
            "functions": fun_meta,
        }

    def format_modules(self, args: dict) -> dict:

        res = args.copy()
        for key, value in args.items():
            # ipdb.set_trace()
            if type(value) == dict and "module" in value:

                value["module"] = value["module"].replace(
                    ".".join([self.root_module, self.type_module, ""]), ""
                )
                res[key] = value

        return res

    def generate_class_metadata(self, klass):

        # ipdb.set_trace()
        args, errors = get_function_args(klass[1].__init__, {})
        # ipdb.set_trace()
        args = self.format_modules(args)
        return {
            "class_name": klass[0],
            "module": self.local_module,
            "params": args,
            "errors": errors,
        }

    def generate_function_metadata(self, function):
        args, errors = get_function_args(function[1], {})
        args = self.format_modules(args)
        return {
            "function_name": function[0],
            "module": self.local_module,
            "params": args,
            "errors": errors,
        }

    def __get_local_module(self):
        return __import__(
            f"{self.root_module}.{self.type_module}.{self.local_module}",
            fromlist=[self.local_module],
        )

    def __find_functions(self, module):

        return inspect.getmembers(module, inspect.isfunction)

    def __find_classes(self, module):

        return inspect.getmembers(module, inspect.isclass)
