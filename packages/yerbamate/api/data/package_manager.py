import hashlib
import json
import os
import validators
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
        ipdb.set_trace()
        pass

    def __download_package(self, url):

        # just git url
        base_git_url = "/".join(url.split("/")[:7])

        # ipdb.set_trace()

        url_hash = hashlib.sha1(base_git_url.encode("utf-8")).hexdigest()

        # print("downloading url", url)

        output_path = self.get_path(url_hash)

        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)

        # print("Cloning repository to {}".format(output_path))

        output_dir = os.path.join(os.getcwd(), output_path)

        # print("Cloning into {}".format(output_dir))

        download(url, output_dir=output_dir)
