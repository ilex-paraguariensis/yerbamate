import json
import os
import re
import sys

import tabulate

from .module_manager import ModuleManager
from .utils.exp_util import get_relative_imports
from .utils.git_util import parse_url_from_git
from .sources.remote import RemoteDataSource
from .sources.local.local import LocalDataSource
from pipreqs import pipreqs

from .package import Package
from typing import Optional
import ipdb


class ModuleRepository:
    def __init__(self, config, run_local_api_server: bool = False):
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
            self.__export()
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
            and not ".egg>=info" in line
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

    def __generate_deps_in_depth(self, root_path):
        # init__path = os.path.join(path, "__init__.py")

        for dir in os.listdir(root_path):
            if dir.startswith(".") or dir.startswith("__"):
                continue
            path = os.path.join(root_path, dir)
            if os.path.isdir(path):
                # check if this is a python module
                init__path = os.path.join(root_path, dir, "__init__.py")
                if not os.path.exists(init__path):
                    continue
                # if dir in ["trainers", "experiments", "models", "data"] and
                if not (
                    dir in ["trainers", "experiments", "models", "data"]
                    and self.config.project in root_path
                ):
                    self.__generate_pip_requirements(path)

                self.__generate_deps_in_depth(path)

    def __export(self, *args, **kwargs):
        self.__generate_sub_pip_reqs()

        modules = self.list()

        table = []

        for key, value in modules.items():
            if type(value) is list:
                table.append([{"type": key, "name": name} for name in value])
                # if empty list, type and name are the same
                if len(value) == 0:
                    table.append([{"type": key, "name": key}])
            elif type(value) is dict:
                table.append([{"type": key, "name": name} for name in value.keys()])

        # ipdb.set_trace()

        table = [item for sublist in table for item in sublist]

        # add url to each item in table
        deps = set()

        base_url = parse_url_from_git()
        user_name = base_url.split("/")[3]
        repo_name = base_url.split("/")[4]
        for item in table:
            item[
                "url"
            ] = f"{base_url}{self.config.project}/{item['type']}/{item['name']}"
            item[
                "short_url"
            ] = f"{user_name}/{repo_name}/{self.config.project}/{item['type']}/{item['name']}"

            # if repo name is same as project name
            if repo_name == self.config.project:
                # item["url"] = f"{base_url}/{item['type']}/{item['name']}"
                # get user name from url
                item[
                    "short_url"
                ] = f"{user_name}/{repo_name}/{item['type']}/{item['name']}"

        # read dependencies
        for item in table:
            path = os.path.join(
                self.config.project, item["type"], item["name"], "requirements.txt"
            )
            dep_path = os.path.join(
                self.config.project, item["type"], item["name"], "dependencies.json"
            )

            root_dep_path = os.path.join(
                self.config.project, item["type"], "requirements.txt"
            )

            if os.path.exists(path):
                with open(path, "r") as f:
                    item["dependencies"] = f.readlines()
            if os.path.exists(dep_path):
                with open(dep_path, "r") as f:
                    if "dependencies" in item:
                        item["dependencies"] += json.load(f)["dependencies"]
                    else:
                        item["dependencies"] = json.load(f)["dependencies"]

                    # item["module_dependencies"] = json.load(f)
            if os.path.exists(root_dep_path):
                with open(root_dep_path, "r") as f:
                    item["dependencies"] = f.readlines()

            if "dependencies" in item:
                item["dependencies"] = [
                    dep.replace("\n", "") for dep in item["dependencies"]
                ]

                deps.update(item["dependencies"])

        # remove github urls from dependencies if it
        deps = [
            dep for dep in deps if not ("https://github" in dep and not "+git" in dep)
        ]
        # set index urls should be on top, sort so that --extra-index-url is on top
        deps = sorted(deps, key=lambda x: "--extra-index-url" in x, reverse=True)
        # remove empty lines
        deps = [dep for dep in deps if dep != "\n" or dep != " " or dep != ""]

        # save deps in requirements.txt
        with open("requirements.txt", "w") as f:
            for dep in deps:
                f.write(dep + "\n")

            # create latex table

            # ipdb.set_trace()
            # l_table = [t for t in table if t["type"] == "models"]
            # remove url from table
        ltable = table
        # for item in ltable:
        #     del item["url"]
        #     for dep in item["dependencies"]:
        #         if "--extra" in dep:
        #             item["dependencies"].remove(dep)
        #         # if "https" in dep:

        # create latex table
        # recreate table to remove url
        ltable = []

        # combine dependenices, make a set, remove urls, and save as requirements.txt

        with open("exports.json", "w") as f:
            json.dump(table, f, indent=4)

        for item in table:
            # remove --extra from dep
            if "dependencies" in item:
                # if --extra in dep
                new_dep = []
                for dep in item["dependencies"]:
                    if "--extra" in dep:
                        continue
                    new_dep.append(dep)
                ltable.append(
                    {
                        "name": item["name"],
                        "type": item["type"],
                        "short_url": item["short_url"],
                        "dependencies": new_dep,
                    }
                )
            else:
                ltable.append(
                    {
                        "name": item["name"],
                        "type": item["type"],
                        "short_url": item["short_url"],
                        "dependencies": item["dependencies"],
                    }
                )

        # ipdb.set_trace()

        latex_table = tabulate.tabulate(
            ltable,
            headers="keys",
            tablefmt="latex",
            showindex="never"
            # disable_numparse=False,
        )

        table = tabulate.tabulate(
            table,
            headers="keys",
            tablefmt="github",
            showindex="always",
            disable_numparse=True,
        )

        # save table to export.md

        with open("export.md", "w") as f:
            f.write(table)

        with open("exports.tex", "w") as f:
            f.write(latex_table)

        print("Exported to export.md")

    def __generate_sub_pip_reqs(self):
        root_path = self.config.project
        self.__generate_deps_in_depth(root_path)

        for dir in os.listdir("."):
            if (
                dir.startswith(".")
                or dir.startswith("__")
                or dir == self.config.project
            ):
                continue
            path = os.path.join(".", dir)
            if os.path.isdir(path):
                # check if this is a python module
                init__path = os.path.join(".", dir, "__init__.py")
                if not os.path.exists(init__path):
                    continue
                self.__generate_pip_requirements(path)

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

        relative_imports = [
            module
            for module in relative_imports
            if not any([file in module for file in original_files])
        ]

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

            sister_module_path = [*module.split(".")]

            if os.path.exists(os.path.join(*tpath)):
                # module = parent
                url = "/".join(tpath[:-1])
            elif os.path.exists(os.path.join(*sister_module_path)):
                url = sister_module_path[0] + "/"
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
        # ipdb.set_trace()
        try:
            imports = pipreqs.get_all_imports(path)

            # import_info_remote = pipreqs.get_imports_info(imports)

            import_info_local = pipreqs.get_import_local(imports)
        except Exception as e:
            print(f"Error generating requirements.txt for {path}")
            print(e)
            # raise e
            return {}

        self.__generate_mate_dependencies(path)

        import_info = []

        if path == self.config.project:
            pipreqs.generate_requirements_file(
                "requirements.txt", import_info_local, ">="
            )
            self.__add_index_url_to_requirements("requirements.txt")

        else:
            pipreqs.generate_requirements_file(
                os.path.join(path, "requirements.txt"), import_info_local, ">="
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
