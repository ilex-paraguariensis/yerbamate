import hashlib
import json
import os
import re
from shutil import copytree, rmtree
import validators
from yerbamate.mate_config import MateConfig

from .utils.gitdir import download
import ipdb


class ModuleManager:
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


    def check_auto_install_reqs(self, *args, **kwargs):
        if len(args) < 1:
            return False
        if args[0] == "-y":
            return True

    def check_auto_no_install_reqs(self, *args, **kwargs):
        if len(args) < 1:
            return False
        if args[0] == "-n":
            return True

    def auto_install_manager(self, *args, **kwargs):
        if self.check_auto_install_reqs(*args, **kwargs):
            if len(args) > 1:
                pm = args[1]
                if pm in ["pip", "conda"]:
                    return pm
            else:
                cmd = input("Install with pip or conda? [pip/conda]: ")
                if cmd in ["pip", "conda"]:
                    return cmd

            while cmd not in ["pip", "conda"]:
                cmd = cmd("Install with pip or conda? [pip/conda]: ")
                if cmd in ["pip", "conda"]:
                    return cmd
            
            return None
        return None

    def install_package(self, url: str, *args, **kwargs):

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

                if self.check_auto_install_reqs(*args, **kwargs):
                    pm = self.auto_install_manager(*args, **kwargs)
                    if pm == "pip":
                        os.system(f"pip install -r {requirements_path}")
                        print("")
                    elif pm == "conda":
                        os.system(f"conda install --file {requirements_path}")
                        print("")
                    else:
                        print("Skipping requirements installation")
                    
                elif not self.check_auto_no_install_reqs(*args, **kwargs):
                    cmd = input(
                        "Requirements found. Do you want to install them with pip? [y/conda/n]: "
                    )
                    if cmd == "y":
                        os.system(f"pip install -r {requirements_path}")
                        print("")

                    elif cmd == "conda":
                        os.system(f"conda install --file {requirements_path}")
                        print("")
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
                    self.install_package(dependency, *args, **kwargs)

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

        print(f"Installing {root_module}/{module_name} from {base_git_url}")

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
                print("Deleted existing package at ", dest_path)
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

