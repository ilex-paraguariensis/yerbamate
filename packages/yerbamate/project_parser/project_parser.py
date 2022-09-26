import os
import ipdb
from enum import Enum
from ..utils.bunch import Bunch
import json


class Framework(Enum):
    keras = "keras"
    lightning = "lightning"
    jax = "jax"


class ProjectParser:
    def __init__(self, backbone: str):
        assert (
            backbone in Framework.__members__.keys()
        ), f"Backbone {backbone} not supported. Please use one of {Framework.__members__.keys()}"
        self.backbone = Framework(backbone)
        # loads the correct template (which is in json format) from the backbone_templates folder
        with open(
            os.path.join(
                os.path.dirname(__file__),
                f"backbone_templates/{self.backbone.value}.json",
            )
        ) as f:
            self.template = Bunch(json.load(f))

        assert (
            "experiments" in self.template
        ), "Template must have experiments key"

    @staticmethod
    def _check_template_syntax(template: Bunch):
        if isinstance(template, list):
            assert (
                len(template) >= 1
            ), "Template must have at least one element."
            current_type = type(template[0])
            for element in template[1:]:
                assert (
                    type(element) == current_type
                ), "Template must be homogeneous."
        elif isinstance(template, dict):
            assert (
                len(template) >= 1
            ), "Template must have at least one element."
            for element in template.values():
                ProjectParser._check_template_syntax(element)

    def check_project_structure(self):
        assert (
            "__init__.py" in os.listdir()
        ), "Project must have __init__.py file"
        assert sorted(self.template.keys()) == sorted(
            os.listdir()
        ), "Project structure does not match the template for backbone {self.backbone.value}.\nShould be {self.template.keys()}"
        # checks that all items in listdir() are folders
        for key, val in self.template:
            if isinstance(val, list):
                assert os.path.isdir(key), f"{key} should be a directory"
                dir_type = type(val[0])  # they all have te same type
                if dir_type == dict:
                    # check that the subdir is a module
                    assert os.path.exists(
                        os.path.join(key, "__init__.py")
                    ), f"Folder {key} is not a module"
                    folder_template = self.template[key]
                    for sub_key in os.listdir(key):
                        subdir_path = os.path.join(key, sub_key)
                        # check if the templates says it shuld be a module
                        if "module" in folder_template:
                            # first check that its a module
                            assert (
                                os.path.isdir(subdir_path)
                                or sub_key == "__init__.py"
                            ), f"{sub_key} is not a folder"

    def check_bombillas(self):
        for experiment in os.listdir("experiments"):
            pass

    def _assert_modules_match(self, template_module, project_module):
        pass

    def _parse_config(self, config: Bunch):
        pass
