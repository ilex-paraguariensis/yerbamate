import os

import sys, inspect

from ..sources.local import LocalDataSource

from .metadata import BaseMetadata, Metadata

from ..package import Package
from bombilla import Bombilla
import ipdb
import json
from dirhash import dirhash

from .utils import get_function_args, find_in_bombilla_dict
from .doc_parser import parse_docs


class ModuleMetadataGenerator:
    def __init__(
        self,
        module_paths: list[str],
        base_metadata: BaseMetadata,
        local_data_source: LocalDataSource,
    ):

        self.root_module = module_paths[0]
        self.type_module = module_paths[1]
        # self.local_module = module_paths[-1]

        # print("Generating metadta, module paths: ", module_paths)

        self.module_paths = module_paths

        self.base_metadata = base_metadata.copy()
        self.base_metadata.update(module_path=module_paths[1:], root_module=None)
        self.local_data_source = local_data_source

        self.module_path = os.path.join(*module_paths)

        self.module = ".".join(module_paths)

        self.local_module = ".".join(module_paths[1:])

        self.module_files = os.listdir(os.path.join(*module_paths))

    def get_possible_modules(self):

        # Automatically adds the root module to the path, so data/loaders can be imported
        return [
            ".".join([self.root_module, self.module]),
            self.module,
            # ".".join([self.root_module, self.type_module, self.local_module]),
            # ".".join([self.type_module, self.local_module]),
        ]

    def search_experiments_for_defaults(self, module, function_name):

        experiments = self.local_data_source.list("experiments")

        samples = []

        for experiment in experiments:

            conf, _ = self.local_data_source.load_experiment(experiment)
            # ipdb.set_trace()

            sample = find_in_bombilla_dict(conf, module, function_name)
            if sample:
                samples += [{"sample": sample, "experiment": conf}]

        return samples

    def update_metadata(self):

        # update URL to point to the right module
        # addition = self.module_paths + [""]
        url_addition = "/".join(self.module_paths + [""])
        new_url = self.base_metadata.url + url_addition
        type = self.type_module
        self.base_metadata.update(url=new_url, type=type)

    def read_metadata(self):
        json_path = os.path.join(self.module_path, "metadata.json")

        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                try:
                    return Metadata(**json.load(f))
                except:
                    return None

        return None

    def generate(self, rewrite=False):

        self.module = self.__get_local_module()

        classes = self.__find_classes(self.module)
        functions = self.__find_functions(self.module)

        # No Metadata for empty modules
        if len(classes) == 0 and len(functions) == 0:
            return {}

        hash = self.__calculate_module_hash()

        old_meta = self.read_metadata()

        # print("rewriting", rewrite)

        if old_meta != None and old_meta.hash == hash and not rewrite:

            return old_meta.to_dict()

        # ipdb.set_trace()

        meta = [self.generate_class_metadata(klass) for klass in classes]

        fun_meta = [self.generate_function_metadata(function) for function in functions]

        self.update_metadata()

        dependencies = self.__generate_pip_dependencies()

        results = {
            "exports": {
                "classes": meta,
                "functions": fun_meta,
            },
            "dependencies": {
                "pip": dependencies,
            },
        }
        self.base_metadata.add(**results)

        self.base_metadata.update(hash=hash, experiments=None)

        if len(meta) != 0 or len(fun_meta) != 0:
            self.save_metadata()

        return self.base_metadata.to_dict()

    def save_metadata(self):

        json_path = os.path.join(self.module_path, "metadata.json")

        with open(json_path, "w") as f:
            f.write(str(self.base_metadata))

    def format_modules(self, args: dict) -> dict:

        res = args.copy()
        for key, value in args.items():
            if type(value) == dict and "module" in value:

                # shorterns the module name
                value["module"] = value["module"].replace(
                    ".".join([self.root_module, self.type_module, ""]), ""
                )
                res[key] = value

        return res

    def generate_class_metadata(self, klass):

        # ipdb.set_trace()
        args, errors = get_function_args(klass[1].__init__, {})
        # docs = parse_docs(klass[1].__init__)

        args = self.format_modules(args)

        defualts = self.search_experiments_for_defaults(klass[1], klass[0])

        result = {
            "class_name": klass[0],
            "module": self.local_module,
            "params": args,
            "samples": defualts,
            "errors": errors,
            # "docs": docs,
        }

        # remove non and empty values
        result = {k: v for k, v in result.items() if v and v != "None" and v != []}

        return result

    def generate_function_metadata(self, function):
        args, errors = get_function_args(function[1], {})
        # docs = parse_docs(function[1])
        args = self.format_modules(args)

        defualts = self.search_experiments_for_defaults(function[1], function[0])

        result = {
            "function_name": function[0],
            "module": self.local_module,
            "params": args,
            "samples": defualts,
            "errors": errors,
            # "docs": docs,
        }

        # remove non and empty values
        result = {k: v for k, v in result.items() if v and v != "None" and v != []}

        return result

    def __generate_pip_dependencies(self):
        from pipreqs import pipreqs

        # slows down mate, FIX THIS

        imports = pipreqs.get_all_imports(self.module_path)
        import_info_remote = pipreqs.get_imports_info(imports)
        import_info_local = pipreqs.get_import_local(imports)

        import_info = []

        for im in import_info_local:

            name = im["name"]
            version = im["version"]

            res = {
                "name": name,
                "version": version,
            }

            for remote in import_info_remote:
                if remote["name"] == name:
                    lastVersion = remote["version"]
                    res["last_version"] = lastVersion

            import_info.append(res)

        return import_info

    def __get_local_module(self):
        return __import__(
            f"{self.module}",
            fromlist=[self.module_paths[-1]],
        )

    def __find_functions(self, module):

        return inspect.getmembers(module, inspect.isfunction)

    def __find_classes(self, module):

        return inspect.getmembers(module, inspect.isclass)

    def __calculate_module_hash(self):
        path = os.path.join(*self.module_paths)

        hash = dirhash(path, "sha1", ignore=["*.pyc", "*.json", "__pycache__"])
        # ipdb.set_trace()

        return hash
