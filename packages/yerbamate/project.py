import os
import ipdb
from rich import print
from rich.tree import Tree
from .console import console
from .experiment import Experiment
from .mate_modules import colors, modules
import ast


class Module:
    def __init__(self, root_dir: str, optional=False, check_exports=False):
        assert isinstance(root_dir, str)
        self._root_dir = root_dir
        self._name = os.path.basename(root_dir)
        # checks that the name is python-friendly
        self.__errors = []
        assert (
            self._name.isidentifier()
        ), f"Module name {self._name} is not a valid python identifier. Please rename the module folder to something python friendly (no spaces, '-' or strange characters)"
        if os.path.exists(root_dir):
            assert os.path.isdir(root_dir), "root_dir must be a directory"
            assert os.path.isfile(
                os.path.join(root_dir, "__init__.py")
            ), f"{self.relative_path()} must be a python module.\n You should add an __init__.py and import the functions/classes you want to export from there."
        else:
            assert optional, f"root_dir {root_dir} does not exist"

        self._exports = self.__collect_exports()
        if check_exports and len(self._exports) == 0:
            self.__errors.append(
                f"No exports found in {self.relative_path()}. Consider exporting with 'mate export <module>'"
            )

    @property
    def errors(self):
        return self.__errors

    @property
    def name(self):
        return self._name

    @property
    def exports(self):
        return self._exports

    def __collect_exports(self) -> dict[str, ast.ImportFrom]:
        with open(os.path.join(self._root_dir, "__init__.py"), "r") as f:
            tree = ast.parse(f.read())
        exports = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if not (node.level == 1):
                    self.__errors.append(
                        f"Only relative imports are allowed in {self.relative_path()} (for shearability)."
                    )
                # the module name is the key
                # the value is the import node
                exports[node.module] = node

        return exports

    def relative_path(self):
        return ".".join(self._root_dir.replace(os.getcwd(), "").split(os.sep)[2:])

    def __eq__(self, other):
        assert isinstance(other, Module) or isinstance(other, str)
        if isinstance(other, Module):
            return self._root_dir == other._root_dir
        else:
            return self._name == other

    def __str__(self):
        return self._name

    def __repr__(self):
        return f"Module(name={self._name})"

    def __contains__(self, item):
        return item in self.exports.keys()

    def __getitem__(self, item):
        assert isinstance(item, str)
        assert not "." in item, ipdb.set_trace()  # "Cannot access submodules"
        assert item in self, f"{item} not found in {self.relative_path()}"
        return self._exports[item]

    def to_tree(self):
        parent = self.relative_path().split(".")[0]
        tree = Tree(parent, style=f"bold underline {modules[parent].color}")
        node = tree.add(self.name)
        val = self.exports
        for v in val.values():
            node.add(v.names[0].name)
        return tree


class ModulesDict(Module, dict):
    def __init__(self, root_dir: str, optional=False):
        # lists all the subdirectories and asserts that they are python modules
        if os.path.exists(root_dir):
            subdirs = [
                os.path.join(root_dir, d)
                for d in os.listdir(root_dir)
                if os.path.isdir(os.path.join(root_dir, d)) and not d.startswith("_")
            ]
            # assert all(
            #     os.path.isfile(os.path.join(d, "__init__.py")) for d in subdirs
            # ), f"{d} must be a python module"
            files = [
                os.path.join(root_dir, f)
                for f in os.listdir(root_dir)
                if os.path.isfile(os.path.join(root_dir, f)) and f != "__init__.py"
            ]
            if len(files) > 0:
                console.print(
                    f"[{colors.error} bold]ERROR[/{colors.error} bold]: [yellow]found file(s) in {root_dir}: \n\t{files}[yellow]\nPlease move them to a subfolder or delete them."
                )
                exit(1)

            for d in subdirs:
                self[os.path.basename(d)] = Module(d, check_exports=True)
        else:
            if not optional:
                print(f"WARNING: {root_dir} does not exist", "yellow")
                os.makedirs(root_dir)
                with open(os.path.join(root_dir, "__init__.py"), "w") as f:
                    f.write("")
                print(f"Created {root_dir}")
        super().__init__(root_dir)

    def __str__(self):
        return f"ModulesDict(name={self._name}, submodules={set(self.keys())})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {k: v for k, v in self.items()}

    def __contains__(self, item: str):
        return item in self.keys()

    def __getitem__(self, item):
        assert isinstance(item, str)
        cur, *path = item.split(".")
        assert cur in self, ipdb.set_trace()  # f"Invalid submodule '{self.name}.{cur}'"
        selected = tuple((k, v) for k, v in self.items() if k == cur)[0][1]
        return selected if (len(path) == 0) else selected[".".join(path)]


"""
class NestedModule(ModulesDict):
    def __init__(self, root_dir: str, submodule_names: tuple[str, ...]):
        super().__init__(root_dir)
        # checks that the submodules names are the same as the subdirectories
        # in the root directory
        assert set(submodule_names) == set(
            self.keys()
        ), f"Invalid submodules found in {root_dir}, expected {submodule_names}"
        # makes the submodules accessible as attributes
        for name in submodule_names:
            setattr(self, name, ModulesDict(os.path.join(root_dir, name)))

    def __str__(self):
        dict_str = set(tuple(k for k in self.__dict__.keys() if not k.startswith("_")))
        return f"NestedModule(name={self._name}, submodules={dict_str})"

    def __repr__(self):
        return self.__str__()
"""


class ExperimentsModule(Module, dict):
    def __init__(self, root_dir: str):
        super().__init__(root_dir)
        for path in self.__list_experiments():
            # local_path = ".".join(name[:-3].split(os.sep)[-3:])
            self[os.path.basename(path)[:-3]] = Experiment(path)  # local_path
            # check_experiment(name)

    def __list_experiments(self):
        assert all(
            os.path.isfile(os.path.join(self._root_dir, name))
            for name in os.listdir(self._root_dir)
            if not name.startswith("_")
        ), f"Invalid experiments found in {self._root_dir}"
        assert all(
            name.endswith(".py")
            for name in os.listdir(self._root_dir)
            if not name.startswith("_")
        ), "All files in experiments/ must be python files"
        return [
            os.path.join(self._root_dir, name)
            for name in os.listdir(self._root_dir)
            if not name.startswith("_") and name.endswith(".py")
        ]

    def __str__(self):
        return f"ExperimentsModule(experiments={set(self.keys())})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {k: e for k, e in self.items()}

    def __getitem__(self, path: str):
        assert isinstance(path, str)
        assert not "." in path, "Experiments don't have submodules"
        assert path in self.keys()
        selected = tuple((k, v) for k, v in self.items() if k == path)[0][1]
        return selected


class MateProject(Module):
    def __init__(self, root_dir: str):
        self.models = ModulesDict(os.path.join(root_dir, "models"))
        self.data_loaders = ModulesDict(os.path.join(root_dir, "data_loaders"))
        self.trainers = ModulesDict(os.path.join(root_dir, "trainers"), optional=True)
        # self.trainers = NestedModule(
        #     os.path.join(root_dir, "trainers"), ("trainers", "metrics")
        # )
        # self.data = NestedModule(
        #     os.path.join(root_dir, "data"), ("loaders", "preprocessing")
        # )
        self.experiments = ExperimentsModule(os.path.join(root_dir, "experiments"))
        super().__init__(root_dir)
        self.__white_list = ["mate.json", ".mate"]
        self.check_no_additional_dirs()

    def check_no_additional_dirs(self):
        for name in os.listdir(self._root_dir):
            if (
                not name.startswith("__")
                and (name not in self.__dict__)
                and (name not in self.__white_list)
            ):
                raise ValueError(
                    f"Found additional file or directory '{name}' in {self._root_dir}. Please remove it."
                )

    def to_dict(self):
        return {
            k: v.to_dict() for k, v in self.__dict__.items() if not k.startswith("_")
        }

    def clone(self, path: str, name: str):
        assert isinstance(path, str)
        assert isinstance(name, str)
        assert "." in path, "path must be a valid python path (e.g. models.resnet)"
        full_source_path = os.path.join(self._root_dir, path.replace(".", os.sep))
        full_target_path = os.path.join(
            self._root_dir, *path.split(".")[:-1], name.replace(".", os.sep)
        )
        if path.startswith("experiments"):
            full_source_path += ".py"
            full_target_path += ".py"

        assert os.path.exists(
            full_source_path
        ), f"Invalid path {path} (full path: {full_source_path})"
        assert not os.path.exists(
            full_target_path
        ), f"Path {full_target_path} already exists. Try with a different name?"
        os.system(f"cp -r {full_source_path} {full_target_path}")

    def remove(self, target: str):
        assert isinstance(target, str)
        full_target_path = os.path.join(self._root_dir, target.replace(".", os.sep))
        if target.startswith("experiments"):
            full_target_path += ".py"
        assert os.path.exists(
            full_target_path
        ), f"Invalid path {target} (full path: {full_target_path})"
        os.system(f"rm -r {full_target_path}")

    def rename(self, source: str, destination: str):
        assert isinstance(source, str)
        assert isinstance(destination, str)
        assert (
            "." in source
        ), "source must be a valid python path (e.g. models.resnet) and cannot be a root directory"
        full_source_path = os.path.join(self._root_dir, source.replace(".", os.sep))
        full_destination_path = os.path.join(
            self._root_dir, *source.split(".")[:-1], destination.replace(".", os.sep)
        )
        if source.startswith("experiments"):
            full_source_path += ".py"
            full_destination_path += ".py"

        assert os.path.exists(
            full_source_path
        ), f"Invalid path {source} (full path: {full_source_path})"
        assert not os.path.exists(
            full_destination_path
        ), f"Path {full_destination_path} already exists. Try with a different name?"
        os.system(f"mv {full_source_path} {full_destination_path}")

    def create(self, path: str, name: str):
        assert isinstance(path, str)
        assert isinstance(name, str)
        assert (
            name.isidentifier()
        ), "name must be a valid python identifier. Please use snake_case"
        full_target_path = os.path.join(
            self._root_dir, path.replace(".", os.sep), name.replace(".", os.sep)
        )
        assert not os.path.exists(
            full_target_path
        ), f"Path {full_target_path} already exists. Try with a different name?"
        if not path == "experiments":
            os.system(f"mkdir -p {full_target_path}")
            os.system(f"touch {full_target_path}/__init__.py")
        else:
            os.system(f"touch {full_target_path}.py")

    def __str__(self):
        dict_str = set(tuple(k for k in self.__dict__.keys() if not k.startswith("_")))
        return f"MateProject(name={self._name}, submodules={dict_str})"

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item: str):
        assert isinstance(item, str)
        cur, *rest = item.split(".")
        assert cur in self.__dict__, f"Invalid key {cur}"
        if len(rest) == 0:
            return self.__dict__[cur]
        else:
            return self.__dict__[cur][".".join(rest)]
