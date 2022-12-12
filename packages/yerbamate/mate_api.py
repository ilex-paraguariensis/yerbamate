import os
import sys
import json
import glob
from yerbamate.mate_config import MateConfig
from .runtime import MateRuntime
from .git_manager import GitManager

# from .data.package_repository import PackageRepository
from rich import print
from rich.tree import Tree
from rich.text import Text
from rich.table import Table
from .console import console
import ipdb
from . import io
from .project import MateProject
from .mate_modules import colors, modules

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
        os.system(f"rm -rf .mate")

    def __get_results_dict(self):
        import glob

        results_folders = [
            folder
            for folder in glob.glob(os.path.join(self.config.results_folder, "*"))
            if os.path.isdir(folder)
        ]
        all_results = {}
        for folder in results_folders:
            results = glob.glob(os.path.join(folder, "result.json"))
            experiment_name = folder.split(os.sep)[-1]
            if len(results) > 0:
                with open(results[0], "r") as f:
                    all_results[experiment_name] = json.load(f) | {
                        "experiment": experiment_name
                    }
        return all_results

    def to_tree(self) -> Tree:
        vals = self.project.to_dict()
        # turns this nested dict into a rich tree
        tree = Tree(
            Text("🧉 ") + Text(self.project._name, "underline"), style="bold #32CD30"
        )

        results = self.__get_results_dict()
        for k, v in vals.items():
            # add a node for the key using the funciton .add() removes the underline style
            # and adds the matching color
            node = tree.add(k, style=f"bold {modules[k].color}")
            for k2, e in v.items():
                text = Text(k2)
                if k == "experiments":
                    if k2 in results:
                        text += Text(f"☑", "bold #00FF00")

                if len(e.errors) > 0:
                    text += Text(f"❌", f"bold {colors.error}")
                node.add(text)

        return tree

    def show(self, path: str):
        node = self.project[path]
        tree = node.to_tree()
        console.print(tree)
        if len(node.errors) > 0:
            console.print(f"[{colors.error} bold]ERRORS:[/{colors.error} bold]")
            for e in node.errors:
                console.print(
                    f"    [{colors.error}]❌[/{colors.error}][yellow]{e}[/yellow]"
                )

    def export(self, source: str):
        assert isinstance(source, str), "Source must be a string"
        assert "." in source, "Source must be a path"
        module_root = os.path.join(
            self.project._name, os.sep.join(source.split(".")[:2])
        )
        assert os.path.exists(
            module_root
        ), f"Module {module_root.replace(os.sep, '.')} does not exist"
        target_file = os.path.join(module_root, "__init__.py")
        relative_path = ".".join(source.split(".")[2:-1])
        to_export = source.split(".")[-1]
        import_statement = f"from .{relative_path} import {to_export}\n"
        # checks that the import statement is not already in the file
        with open(target_file, "r") as f:
            if import_statement not in f.read():
                with open(target_file, "a") as f:
                    f.write(import_statement)
                console.print(
                    f"  ✅[green]Exported {to_export} from {source} to {target_file}[/green], ('{import_statement}')"
                )
            else:
                print(f"{to_export} already exported, skipping.")

    def results(self) -> Table | None:

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
        if len(keys) > 0:
            keys.remove("experiment")
            keys = ["experiment"] + keys
            # create a table with the keys as columns
            table = []
            for result in all_results:
                row = []
                for key in keys:
                    row.append(result.get(key, ""))
                table.append(row)
            t = Table(title="Results", show_header=True, header_style="bold #00FF00")
            for key in keys:
                t.add_column(key)
            for row in table:
                t.add_row(*[str(x) for x in row])
            return t

    def rename(self, target: str, destination: str):
        self.project.rename(target, destination)

    def install(self, url: str):
        git = GitManager.from_url(self.project._name, url)
        git.clone(os.path.join(self.mate_dir, "tmp"))
        print(git)

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
        pass

    def test(self, experiment_name: str):
        assert (
            experiment_name in self.project.experiments
        ), f"Experiment:{experiment_name} not found"
        save_dir = os.path.join(self.config.results_folder, experiment_name)
        checkpoint_path = os.path.join(save_dir, "checkpoints")
        if not os.path.exists(checkpoint_path):
            os.makedirs(checkpoint_path)
        runtime = MateRuntime(
            command="test",
            save_dir=save_dir,
            checkpoint_path=checkpoint_path,
            runtime_save_path=os.path.join(self.mate_dir, "runtime.json"),
        )
        runtime.save()
        if self.config.verbose:
            print(runtime)
        os.system(f"python -m {self.project.experiments[experiment_name]}")

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
