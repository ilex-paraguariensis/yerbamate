import json
import os
import re
import sys

from .module_manager import ModuleManager
from .utils.exp_util import get_relative_imports
from .utils.git_util import parse_url_from_git
from ...mate_config import MateConfig
from .sources.remote import RemoteDataSource
from .sources.local.local import LocalDataSource
from pipreqs import pipreqs

from .package import Package
from typing import Optional
import ipdb


class ModuleRepository:
    def __init__(self, config: MateConfig, run_local_api_server: bool = False):
        self.config = config
        self.package_manager = ModuleManager(config)
        self.remote = RemoteDataSource()
        self.local = LocalDataSource(config)
        # self.__generate_pip_requirements(self.config.project)

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
            print(
                "Project {} created, run `cd {}` to enter the project folder".format(
                    project_name, project_name
                )
            )

        except Exception as e:
            print(e)

    def install_url(self, url: str, *args, **kwargs):

        self.package_manager.install_package(url, *args, **kwargs)

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
            if not os.path.isdir(path) or folder == "__pycache__" or "." in folder:
                continue
            init__py = os.path.join(path, "__init__.py")
            if not os.path.exists(init__py):
                with open(init__py, "w") as f:
                    f.write("")
                print(f"Created {init__py}")
            self.__generate__init__(path)

    def __parse_index_urls(self, reqs: list[str]):
        urls = {
            "torch": "https://download.pytorch.org/whl/torch_stable.html",
            "jax": "https://storage.googleapis.com/jax-releases/jax_releases.html",
        }
        indexes = set()
        for req in reqs:
            if "torch" in req:
                indexes.add(urls["torch"])
            if "jax" in req:
                indexes.add(urls["jax"])

        return indexes

    def __add_index_url_to_requirements(self, path: str):
        with open(os.path.join(path), "r") as f:
            lines = f.readlines()
        linecount = len(lines)
        lines = [
            line
            for line in lines
            if not ".egg>=info" in line
            and not ".egg==info" in line
            and not ".egg~=info" in line
        ]

        # remove +cu{numbers} version form lines
        # regex for numbers with at least 1 digit
        regex = re.compile(r"\+cu\d+")
        lines = [regex.sub("", line) for line in lines]

        urls = self.__parse_index_urls(lines)
        if len(urls) > 0:
            with open(os.path.join(path), "w") as f:
                for url in urls:
                    f.write(f"--extra-index-url {url}\n")
                for line in lines:
                    f.write(line)
        elif linecount != len(lines):
            with open(os.path.join(path), "w") as f:
                for line in lines:
                    f.write(line)

    def __generate_sub_pip_reqs(self):

        root_path = self.config.project
        self.__generate_pip_requirements(root_path)

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
        original_files = [file.replace(".py", "") for file in files] + [
            f for f in os.listdir(path) if "__" not in f
        ]

        relative_imports = [get_relative_imports(os.path.join(path, f)) for f in files]
        # flatten array to unique set
        relative_imports = set(
            [item for sublist in relative_imports for item in sublist]
        )

        # remore original files from relative imports
        # ipdb.set_trace()
        # importz = []
        # for module in relative_imports:
        #     # if any original file is in the module name, remove it
        #     if any([file in module for file in original_files]):
        #         continue
        #     importz.append(module)

        # refactor above code
        relative_imports = [
            module
            for module in relative_imports
            if not any([file in module for file in original_files])
        ]

        # ipdb.set_trace()
        #

        url_git = parse_url_from_git()

        if url_git is None:
            print("No git url found, skipping dependencies.json")
            return

        deps = set()
        for module in relative_imports:

            if module.endswith(".py"):
                continue

            # if its a python file, return parent module

            tpath = [self.config.project, *module.split(".")]
            tpath[-1] = tpath[-1] + ".py"

            # ipdb.set_trace()

            if os.path.exists(os.path.join(*tpath)):
                # module = parent
                url = "/".join(tpath[:-1])
            else:
                url = self.config.project + "/" + module.replace(".", "/")

            if url_git:
                url = url_git + url
            deps.add(url)

        if len(deps) == 0:
            return

        try:

            deps_json = os.path.join(path, "dependencies.json")
            if os.path.exists(deps_json):
                with open(deps_json, "r") as f:
                    # ipdb.set_trace()
                    deps_json = json.load(f)
                    if "env" in deps_json:
                        env = deps_json["env"]
                    else:
                        env = {}

            else:
                env = {}
        except Exception as e:
            print(f"Error reading {path}/dependencies.json, skipping env")
            env = {}

        with open(os.path.join(path, "dependencies.json"), "w") as f:
            deps = {"dependencies": list(deps), "env": env}
            json.dump(deps, f, indent=4)
            print(f"Generated dependencies.json for {path}")

    def __generate_pip_requirements(self, path):

        imports = pipreqs.get_all_imports(path)
        # import_info_remote = pipreqs.get_imports_info(imports)
        import_info_local = pipreqs.get_import_local(imports)

        self.__generate_mate_dependencies(path)

        import_info = []

        if path == self.config.project:
            pipreqs.generate_requirements_file(
                "requirements.txt", import_info_local, "~="
            )
            self.__add_index_url_to_requirements("requirements.txt")

        else:
            pipreqs.generate_requirements_file(
                os.path.join(path, "requirements.txt"), import_info_local, "~="
            )
            self.__add_index_url_to_requirements(os.path.join(path, "requirements.txt"))
            print(f"Generated requirements.txt for {path}")

        for im in import_info_local:

            name = im["name"]
            version = im["version"]

            res = {
                "name": name,
                "version": version,
            }

            import_info.append(res)

        return {"pip": import_info}

    def list(self, module: str = None):
        if module == None:
            return self.local.summary()
        return self.local.list(module)

    def get_mate_summary(self):
        return self.local.summary()

    def install_package(self, package: Package):
        self.local.install_package(package)
