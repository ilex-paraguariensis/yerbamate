import hashlib
import json
import os
import re
from shutil import copytree, rmtree
import validators
from yerbamate.api.data.metadata.metadata import Metadata
from yerbamate.mate_config import MateConfig

from .utils.gitdir import download
import ipdb


class PackageManager:
    root_path: str = ""

    def __init__(self, conf: MateConfig):
        self.conf = conf

        self.init_package_cache()

    def init_package_cache(self):

        folder_name = ".mate"
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        self.root_path = os.path.join(os.getcwd(), folder_name)

    def get_path(self, *args):
        return os.path.join(self.root_path, *args)

    def read_history(self):

        history_path = self.get_path("history.json")
        if not os.path.exists(history_path):
            return []

        with open(history_path, "r") as f:
            return json.load(f)

    def install_package(self, url):

        if url.count("/") > 3 and "github.com" not in url:

            url = url.split("/")
            # oalee/deep-vision/deepnet/models/resnet to https://github.com/oalee/deep-vision/tree/main/deepnet/models/resnet
            url = f"https://github.com/{url[0]}/{url[1]}/tree/main/{'/'.join(url[2:])}"

        assert validators.url(url), "Invalid url"

        package_install_dst = self.__install_package(url)

        # check for requirements.txt
        if package_install_dst:
            requirements_path = os.path.join(package_install_dst, "requirements.txt")
            if os.path.exists(requirements_path):
                cmd = input(
                    "Requirements found. Do you want to install them with pip? [y/conda/n]: "
                )
                if cmd == "y":
                    os.system(f"pip install -r {requirements_path}")
                elif cmd == "conda":
                    os.system(f"conda install --file {requirements_path}")
                else:
                    print("Skipping requirements installation")
            else:
                print("No requirements found. Manually check and install dependencies.")
            # read dependencies.json
            dependencies_path = os.path.join(package_install_dst, "dependencies.json")
            if os.path.exists(dependencies_path):
                with open(dependencies_path, "r") as f:
                    dependencies = json.load(f)
                for dependency in dependencies["dependencies"]:
                    # ipdb.set_trace()
                    self.install_package(dependency)

        # update history

        print(f"Module installed at {package_install_dst}")

    def __install_package(self, url):

        # just git url
        base_git_url = "/".join(url.split("/")[:7])

        url_hash = hashlib.sha1(base_git_url.encode("utf-8")).hexdigest()

        output_path = self.get_path(url_hash)
        output_dir = output_path

        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)

        root_module = url.split("/")[-2]
        module_name = url.split("/")[-1]

        if root_module in ["models", "data", "experiments", "trainers"]:
            dest_path = os.path.join(
                os.getcwd(), self.conf.project, root_module, module_name
            )

        else:
            print("Could not automatically determine the module type. Please specify.")
            command = input(f"Is {root_module}/{module_name} Correct [y,n]?")
            if command == "y":
                dest_path = os.path.join(
                    os.getcwd(), self.conf.project, root_module, module_name
                )
            else:
                dest_path = input(
                    "Please specify the correct path: (e.g. models.my_model)"
                )
                while dest_path.count(".") < 0:
                    dest_path = input(
                        "Please specify the correct path: (e.g. models.my_model) "
                    )
                dest_path = dest_path.split(".")
                dest_path = os.path.join(os.getcwd(), self.conf.project, *dest_path)

        while os.path.exists(dest_path):
            cmd = input(
                "Package already exists, options: [o]verwrite, [c]ancel, [r]ename: "
            )

            if cmd == "o":
                rmtree(dest_path)
                break

            elif cmd == "c":
                return

            elif cmd == "r":
                dest_path = input(
                    "Please specify the correct path: (e.g. models.my_model) "
                )
                while dest_path.count(".") < 0:
                    dest_path = input(
                        "Please specify the correct path: (e.g. models.my_model) "
                    )
                    print(dest_path.count("."))
                dest_path = dest_path.split(".")
                dest_path = os.path.join(os.getcwd(), self.conf.project, *dest_path)
                break

        print(f"Downloading {url}")

        download(url, output_dir=output_dir)

        src_module = url.split("tree")[1].split("/")[2:]
        src_module = os.path.join(output_dir, *src_module)

        copytree(src_module, dest_path)
        rmtree(output_dir)
        return dest_path

    def __get_destination_path(self, metadata: Metadata):

        path = [self.conf["project"]] + metadata.module_path
        path = os.path.join(*path)

        return path

    # check if the name is a valid python module name
    def __validate_module_name(self, name: str):

        # should be a valid python module name

        supported_regex = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
        return supported_regex.match(name)

    def __copy_package(
        self, metadata: Metadata, output_dir: str, module_path_from_git: list
    ):

        dest_path = self.__get_destination_path(metadata)
        src_path = os.path.join(
            output_dir, *module_path_from_git, *metadata.module_path
        )
        while os.path.exists(dest_path):
            cmd = input(
                "Package already exists, options: [o]verwrite, [c]ancel, [r]ename: "
            )

            if cmd == "o":
                rmtree(dest_path)
                break

            elif cmd == "c":
                return

            elif cmd == "r":
                while True:
                    new_name = input("New name: ")
                    if self.__validate_module_name(new_name):
                        metadata.module_path[-1] = new_name
                        dest_path = self.__get_destination_path(metadata)
                        break
                    else:
                        print("Invalid name, try again")

        if not os.path.exists(dest_path):
            # os.makedirs(dest_path, exist_ok=True)
            # copytree(output_dir, path)
            copytree(src_path, dest_path)
            self.__update_metadata(metadata)
            self.__auto_create_init_pys(metadata)
            print(f"Successfully installed package in {dest_path}")

        else:
            print("Package already installed")
            # TODO, update, ask for rename, etc

    # def __copy_installed_package()

    def __find_save_metadata_path(self, metadata: Metadata):

        root_module = self.conf["project"]
        modules = metadata.module_path

        path = os.path.join(root_module, *modules, "fork_metadata.json")
        return path
        pass

    def __auto_create_init_pys(self, metadata: Metadata):

        path = [self.conf["project"]] + metadata.module_path

        for i in range(len(path)):
            init_path = os.path.join(*path[:i], "__init__.py")
            if not os.path.exists(init_path):
                with open(init_path, "w") as f:
                    f.write("")

        #
        #

    def __update_metadata(self, metadata: Metadata):

        # hist_url = metadata.get("history_url", [])

        # hist_url += [metadata.url]

        # metadata["url"] = ""
        # metadata["history_url"] = hist_url

        path = self.__find_save_metadata_path(metadata)

        # assert os.path.exists(path), "metadata.json not found"
        with open(path, "w") as f:
            json.dump(metadata.to_dict(), f, indent=4)

        # pass
