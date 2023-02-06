import json
import os
import sys

from ...api.data.package_manager import PackageManager
from ...api.data.utils.exp_util import get_relative_imports
from ...api.data.utils.git_util import parse_url_from_git
from ...mate_config import MateConfig
from .sources.remote import RemoteDataSource
from .sources.local.local import LocalDataSource
from pipreqs import pipreqs

from .package import Package
from typing import Optional
import ipdb


class PackageRepository:
    def __init__(self, config: MateConfig, run_local_api_server: bool = False):
        self.config = config
        self.package_manager = PackageManager(config)
        self.remote = RemoteDataSource()
        self.local = LocalDataSource(config)
        self.__generate_pip_requirements(self.config.project)
        # self.__generate_sub_pip_reqs()
        # self.metadata_generator = MetadataGenerator(
        #     config.project, config.metadata, self.local
        # )
        # if run_local_api_server:
        #     self.local_server = LocalServer(self.metadata_generator, self.local)

        # TODO: we should refresh the metadata every time we run a command
        # self.generate_metadata()
        # self.metadata: Optional[dict] = None

    @staticmethod
    def init_project(project_name: str):

        if not os.path.exists(project_name):
            os.mkdir(project_name)
            os.chdir(project_name)
        else:
            print("Project already exists")
            sys.exit(1)

        mate_json = os.path.join("mate.json")
        if not os.path.exists(mate_json):
            dic = {
                "project": project_name,
            }
            # create mate.json

            with open(mate_json, "w") as f:
                json.dump(dic, f, indent=4)
        else:
            print("Project already exists")
            sys.exit(1)

        if not os.path.exists(project_name):
            os.mkdir(project_name)
            init__file = os.path.join(project_name, "__init__.py")
            open(init__file, "a").close()
        try:
            folders = ["experiments", "models", "data", "trainers"]
            for folder in folders:
                os.makedirs(os.path.join(project_name, folder), exist_ok=True)
                init__file = os.path.join(project_name, folder, "__init__.py")
                if not os.path.exists(init__file):
                    open(init__file, "a").close()

        except Exception as e:
            print(e)

    def install_url(self, url: str):
        self.package_manager.install_package(url)

    def generate_metadata(self, rewrite: bool = False):

        self.__generate_metadata()

        base_meta = self.config.metadata.base_metadata()
        base_meta["exports"] = self.__export_metadata()
        base_meta["dependencies"] = self.__generate_pip_requirements()
        base_meta["experiments"] = self.local.list("experiments")
        self.config.metadata = base_meta
        self.config.save()

    def __export_metadata(self):
        assert self.metadata is not None, "Metadata shuldn't be None"
        meta = self.metadata

        exports = {k: {} for k in meta.keys()}
        for key, value in meta.items():
            if type(value) == dict:
                for key2, value2 in value.items():
                    if type(value2) == dict:
                        if "url" in value2:
                            exports[key][key2] = value2["url"]
                            continue
                        else:
                            for key3, value3 in value2.items():
                                if type(value3) == dict:
                                    if "url" in value3:
                                        if key2 not in exports[key]:
                                            exports[key][key2] = {}

                                        exports[key][key2][key3] = value3["url"]
                                        continue

        return exports

    def auto(self, command: str, *args):
        if command == "export":
            self.__generate_sub_pip_reqs()
        elif command in ["init", "fix", "i"]:
            self.__generate__init__(self.config.project)

    def __generate__init__(self, root: str = None):
        init__py = os.path.join(root, "__init__.py")
        if not os.path.exists(init__py):
            with open(init__py, "w") as f:
                f.write("")
            print(f"Created {init__py}")

        for folder in os.listdir(root):
            path = os.path.join(root, folder)
            if not os.path.isdir(path) or path == "__pycache__" or "." in folder:
                continue
            init__py = os.path.join(path, "__init__.py")
            if not os.path.exists(init__py):
                with open(init__py, "w") as f:
                    f.write("")
                print(f"Created {init__py}")
            self.__generate__init__(path)

    def __generate_sub_pip_reqs(self):

        for folder in os.listdir(self.config.project):
            path = os.path.join(self.config.project, folder)
            if os.path.isdir(path) and "__" not in folder:
                for subfolder in os.listdir(path):
                    subpath = os.path.join(path, subfolder)
                    if os.path.isdir(subpath) and "__" not in subfolder:
                        self.__generate_pip_requirements(subpath)
                # self.__generate_pip_requirements(path)

    def __generate_mate_dependencies(self, path):
        # ipdb.set_trace()

        files = [f for f in os.listdir(path) if f.endswith(".py") and "__" not in f]
        relative_imports = [get_relative_imports(os.path.join(path, f)) for f in files]
        # flatten array to unique set
        relative_imports = set(
            [item for sublist in relative_imports for item in sublist]
        )

        url_git = parse_url_from_git()

        deps = set()
        for module in relative_imports:
            url = self.config.project + "/" + module.replace(".", "/")
            if url_git:
                url = url_git + url
            deps.add(url)

        if len(deps) == 0:
            return

        with open(os.path.join(path, "dependencies.mate"), "w") as f:
            deps = {"dependencies": list(deps)}
            json.dump(deps, f, indent=4)
            print(f"Generated dependencies.mate for {path}")

    def __generate_pip_requirements(self, path):

        imports = pipreqs.get_all_imports(path)
        # import_info_remote = pipreqs.get_imports_info(imports)
        import_info_local = pipreqs.get_import_local(imports)

        if "experiments" in path:
            self.__generate_mate_dependencies(path)

        import_info = []

        if path == self.config.project:
            pipreqs.generate_requirements_file(
                "requirements.txt", import_info_local, "=="
            )
        else:
            pipreqs.generate_requirements_file(
                os.path.join(path, "requirements.txt"), import_info_local, "=="
            )
            print(f"Generated requirements.txt in {path} folder")

        for im in import_info_local:

            name = im["name"]
            version = im["version"]

            res = {
                "name": name,
                "version": version,
            }

            # for remote in import_info_remote:
            #     if remote["name"] == name:
            #         lastVersion = remote["version"]
            #         res["last_version"] = lastVersion

            import_info.append(res)

        return {"pip": import_info}

    def __generate_metadata(self):
        self.metadata = self.metadata_generator.generate()

    # def list(self, module: str, query: Optional[str] = None):
    #     print(self.local.list(module, query))
    def list(self, module: str, query: Optional[str] = None):
        return self.local.list(module, query)

    def get_mate_summary(self):
        return self.local.summary()
        if self.metadata is None:
            self.__generate_metadata()
        assert self.metadata is not None, "Metadata shuldn't be None"
        summary = {key: val for key, val in self.metadata.items()}
        summary["experiments"] = self.local.get_all_experiments()
        return summary

    def install_package(self, package: Package):
        self.local.install_package(package)

    """
    def query_models(self, query: Optional[str] = None):
        return self.remote.get_models(query)

    def query_trainers(self, query: str = None):
        return self.remote.get_trainers(query)

    def query_datasets(self, query: str = None):
        return self.remote.get_data_loaders(query)

    def install_model(self, model: Package):
        self.local.add_model(model)
    """
