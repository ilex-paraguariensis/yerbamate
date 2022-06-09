import os
from argparse import ArgumentParser


class Mate:
    def __init__(self):
        self.root_folder = ""
        self.__findroot()
        self.models = (
            tuple(
                x
                for x in os.listdir(os.path.join(self.root_folder, "models"))
                if not "__" in x
            )
            if os.path.exists(os.path.join(self.root_folder, "models"))
            else tuple()
        )

    def __findroot(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        cur_folder = os.path.dirname(__file__)
        current_path = os.getcwd()
        self.root_folder = os.path.basename(current_path)
        os.chdir("..")

    def init(self):
        pass

    def create(self, path: str):
        pass

    def remove(self, path: str):
        pass

    def list_models(self):
        print("\n".join(tuple('\t' + m for m in self.models)))

    def clone(self, surce_path: str, target_path: str):
        pass

    def train(self, model: str):
        pass

    def test(self, model: str):
        pass

    def restart(self, model: str):
        pass

    def tune(self, model: str, params: tuple[str, ...]):
        pass

    def exec(self, model: str, file: str = ""):
        pass
