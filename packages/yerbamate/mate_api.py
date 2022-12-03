import os
import sys
import json
from texttable import Texttable
from yerbamate.mate_config import MateConfig
from .runtime import MateRuntime
from yerbamate.utils.bunch import Bunch

# from .data.package_repository import PackageRepository
from typing import Optional, Union
import ipdb
from . import io
from .project import MateProject

"""
MATE API

"""


class MateAPI:
    def __init__(self):
        root, config = io.find_root()
        self.project = MateProject(root)
        self.config: MateConfig = config
        self.mate_dir: str = ".mate"
        if not os.path.exists(self.mate_dir):
            os.makedirs(".mate")

        if self.config.verbose:
            print(self.config)

    @staticmethod
    def init(project_name: str):
        assert not os.path.exists(project_name), "Project directory exists"
        if os.path.exists(".mate"):
            os.system("rm -rf .mate")
            os.makedirs(".mate")
        os.system(
            f"git clone https://github.com/ilex-paraguariensis/deeplearning-project-template .mate"
        )
        os.system(f"mv {os.path.join('.mate', 'my-project')} {project_name}")
        os.system(f"mv {os.path.join('.mate', 'mate.json')} .")
        os.system(f"rm -rf .mate")
        with open("mate.json", "r") as f:
            config = json.load(f)
        config["project"] = project_name
        with open("mate.json", "w") as f:
            json.dump(config, f, indent=4)

    def summary(self):

        import glob

        results_folders = [
            folder
            for folder in glob.glob(os.path.join(self.config.results_folder, "*"))
            if os.path.isdir(folder)
        ]
        all_results = []
        for folder in results_folders:
            results = glob.glob(os.path.join(folder, "result.json"))
            if len(results) > 0:
                with open(results[0], "r") as f:
                    all_results.append(
                        json.load(f) | {"experiment": folder.split(os.sep)[-1]}
                    )
        # collect all the keys contained in all_results dictionaries
        keys = set()
        for result in all_results:
            keys.update(result.keys())
        keys = list(keys)
        keys.remove("experiment")
        keys = ["experiment"] + keys
        # create a table with the keys as columns
        table = []
        for result in all_results:
            row = []
            for key in keys:
                row.append(result.get(key, ""))
            table.append(row)
        t = Texttable()
        t.add_rows([keys] + table)
        print(t.draw())
        # print(json.dumps(all_results, indent=4))

    def generate_metadata(self, rewrite: bool = False):
        return self.repository.metadata_generator.generate(rewrite)

    def install_url(self, url: str):
        self.repository.install_url(url)

    def create(self, path: str, name: str):
        self.project.create(path, name)

    def train(self, experiment_name: str = "default"):
        assert (
            experiment_name in self.project.experiments
        ), f"Experiment:{experiment_name} not found"
        save_dir = os.path.join(self.config.results_folder, experiment_name)
        checkpoint_path = os.path.join(save_dir, "checkpoints")
        if not os.path.exists(checkpoint_path):
            os.makedirs(checkpoint_path)
        runtime = MateRuntime(
            command="train",
            save_dir=save_dir,
            checkpoint_path=checkpoint_path,
            runtime_save_path=os.path.join(self.mate_dir, "runtime.json"),
        )
        runtime.save()
        if self.config.verbose:
            print(runtime)
        os.system(f"python -m {self.project.experiments[experiment_name]}")

    def clone(self, source: str, destination: str):
        self.project.clone(source, destination)

    def restart(self):
        # TODO, this should be in the trainer

        pass

    def test(self):
        # TODO, this should be in the trainer
        self.init_trainer()
        self.validate_params()
        assert self.trainer is not None
        self.trainer.execute("test")

    def sample(self):
        # TODO, this should be in the trainer if its a generative model
        pass

    def set_checkpoint_path(self):
        assert self.exp and self.save_dir, "You must select an experiment first"
        checkpoint_path = os.path.join(self.save_dir, "checkpoints")
        if not os.path.exists(checkpoint_path):
            os.makedirs(checkpoint_path)
        self.checkpoint_path = checkpoint_path

    def remove(self, target: str):
        self.project.remove(target)

    def delete_checkpoints(self):
        assert self.checkpoint_path is not None
        checkpoints = [
            os.path.join(self.checkpoint_path, p)
            for p in os.listdir(self.checkpoint_path)
        ]

        action = "go"
        if len(checkpoints) > 0:
            while action not in ("y", "n", ""):
                action = input(
                    "Checkpiont file exists. Re-training will erase it. Continue? ([y]/n)\n"
                )
            if action in ("y", "", "Y"):
                for checkpoint in checkpoints:
                    os.remove(checkpoint)  # remove all checkpoint files
            else:
                print("Ok, exiting.")
                return
