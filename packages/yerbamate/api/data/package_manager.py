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

        assert validators.url(url), "Invalid url"

        self.__install_package(url)

    def __install_package(self, url):

        self.__download_package(url)

    def __update_downloaded_metadata(self, metadata: Metadata, path: str):

        assert os.path.exists(path), "metadta path does not exist"
        metadata_path = os.path.join(path, "metadata.json")

        with open(metadata_path, "w") as f:
            json.dump(metadata, f)

    def __download_package(self, url):

        # just git url
        base_git_url = "/".join(url.split("/")[:7])

        url_hash = hashlib.sha1(base_git_url.encode("utf-8")).hexdigest()

        output_path = self.get_path(url_hash)

        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)

        output_dir = os.path.join(os.getcwd(), output_path)

        download(url, output_dir=output_dir)
        module_path_from_git = url.split("/")[7:8]

        metadata_path = os.path.join(output_dir, *module_path_from_git, "metadata.json")

        if os.path.exists(metadata_path):
            print(f"No metadata.json found in {metadata_path}")

            with open(metadata_path, "r") as f:
                metadata = Metadata(**json.load(f))
        else:
            print("No metadata.json found.")
            metadata = Metadata(module_path=url.split("/")[8:])

        self.__copy_package(metadata, output_dir, module_path_from_git)

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
                # delete dest_path
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
