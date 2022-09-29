import os
import ipdb
import shutil

try:
    import validators
except ImportError as e:
    print("Please install validators module\n pip install validators")
    exit(1)


class GitUrlParser:
    def __init__(
        self, url: str = "https://github.com/ilex-paraguariensis/yerbamate/tree/v2/src"
    ):
        validators.url(url)
        self.base_url = url.split("tree")[0]
        self.branch = url.split("tree/")[1].split("/")[0]
        self.path = os.path.join(*url.split("tree/")[1].split("/")[1:])
        self.name = self.path.split("/")[-1]

    def clone(
        self, destination: str = "modules", tmp_destination: str = ".mate", force=False
    ):
        # os.makedirs(os.path.join(tmp_destination), exist_ok=True)
        destination = os.path.join(*destination.split("."))
        if os.path.exists(destination):
            if force:
                shutil.rmtree(destination)
            else:
                raise Exception(
                    f"Directory {destination} already exists. Please remove it and try again or use force=True"
                )
        if os.path.exists(tmp_destination):
            shutil.rmtree(tmp_destination)
        os.system(f"git clone -b {self.branch} {self.base_url} {tmp_destination}")
        shutil.rmtree(os.path.join(tmp_destination, ".git"))
        shutil.move(os.path.join(tmp_destination, self.path), destination)
