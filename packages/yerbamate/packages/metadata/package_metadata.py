import os

import sys, inspect

from ..package import Package
import ipdb

from .utils import get_function_args


class ModelMetadataGenerator:
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

        self.module_path = os.path.join(
            self.root_module, self.type_module, self.local_module
        )
        self.module_files = os.listdir(self.module_path)

    def generate(self):
        ipdb.set_trace()
        module = self.__get_local_module()
        classes = self.__find_classes(module)
        functions = self.__find_functions(module)
        return {
            "classes": classes,
            "functions": functions,
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
