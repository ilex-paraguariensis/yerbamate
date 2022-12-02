import os
import ipdb


class Module:
    def __init__(self, root_dir: str):
        assert isinstance(root_dir, str)
        self._root_dir = root_dir
        self._name = os.path.basename(root_dir)
        assert os.path.isdir(root_dir), "root_dir must be a directory"
        assert os.path.isfile(
            os.path.join(root_dir, "__init__.py")
        ), "root_dir must be a python module"

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


class ModulesDict(Module, dict):
    def __init__(self, root_dir: str):
        # lists all the subdirectories and asserts that they are python modules
        subdirs = [
            os.path.join(root_dir, d)
            for d in os.listdir(root_dir)
            if os.path.isdir(os.path.join(root_dir, d)) and not d.startswith("_")
        ]
        assert all(
            os.path.isfile(os.path.join(d, "__init__.py")) for d in subdirs
        ), "root_dir must be a python module"
        # checks that there are no files in the root directory (except __init__.py)
        # prints an error message if there is one (containing the name of the file)
        files = [
            os.path.join(root_dir, f)
            for f in os.listdir(root_dir)
            if os.path.isfile(os.path.join(root_dir, f)) and f != "__init__.py"
        ]
        if len(files) > 0:
            print(f"ERROR: found file in {root_dir}: {files}")

        for d in subdirs:
            self[os.path.basename(d)] = Module(d)
        super().__init__(root_dir)

    def __str__(self):
        return f"ModulesDict(name={self._name}, submodules={set(self.keys())})"

    def __repr__(self):
        return self.__str__()


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


class ExperimentsModule(Module, dict):
    def __init__(self, root_dir: str):
        super().__init__(root_dir)
        for name in self.__list_experiments():
            self[os.path.basename(name)[:-3]] = ".".join(name.split(os.sep))[:-3]

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


class MateProject(Module):
    def __init__(self, root_dir: str):
        self.models = ModulesDict(os.path.join(root_dir, "models"))
        self.trainers = NestedModule(
            os.path.join(root_dir, "trainers"), ("trainers", "metrics")
        )
        self.data = NestedModule(
            os.path.join(root_dir, "data"), ("loaders", "preprocessing")
        )
        self.experiments = ExperimentsModule(os.path.join(root_dir, "experiments"))
        super().__init__(root_dir)

    def __getitem__(self, item):
        assert isinstance(item, str)
        assert item in self.__dict__, f"Invalid submodule {item}"
        return getattr(self, item)

    def __str__(self):
        dict_str = set(tuple(k for k in self.__dict__.keys() if not k.startswith("_")))
        return f"MateProject(name={self._name}, submodules={dict_str})"

    def __repr__(self):
        return self.__str__()
