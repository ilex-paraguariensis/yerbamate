import os
import ipdb
from ...utils.bunch import Bunch
import json


class ProjectParser:
    def __init__(self, backbone):
        self.backbone = backbone
        # loads the correct template (which is in json format) from the backbone_templates folder

    @staticmethod
    def check_project_structure(root_folder: str):
        try:
            assert "mate.json" in os.listdir(
                os.path.join(root_folder, "..")
            ), "No mate.json found in root directory. Check this is a valid mate project."

            os.chdir(root_folder)
            template_name = "lightning"
            path = os.path.join(
                os.path.dirname(__file__),
                "backbone_templates",
                f"{template_name}.json",
            )
            with open(path) as f:
                template = Bunch(json.load(f))

            ProjectParser._check_template_syntax(template)

            assert "experiments" in template, "Template must have experiments key"
            assert "__init__.py" in os.listdir(), "Project must have __init__.py file"
            dirs = os.listdir()
            for key in template.keys():
                if key not in dirs:
                    raise ValueError(f"Project missing folder: {key}")
            # checks that all items in listdir() are folders
            for key, val in template.items():
                if isinstance(val, list):
                    assert os.path.isdir(key), f"{key} should be a directory"
                    dir_type = type(val[0])  # they all have te same type
                    if dir_type == dict:
                        # check that the subdir is a module
                        assert os.path.exists(
                            os.path.join(key, "__init__.py")
                        ), f"Folder {key} is not a module"
                        folder_template = template[key]
                        for sub_key in os.listdir(key):
                            subdir_path = os.path.join(key, sub_key)
                            # check if the templates says it shuld be a module
                            if "module" in folder_template:
                                # first check that its a module
                                assert (
                                    os.path.isdir(subdir_path)
                                    or sub_key == "__init__.py"
                                ), f"{sub_key} is not a folder"
            os.chdir("..")
        except AssertionError as e:
            print(
                f"The project didn't pass the validation. Please check the following:\n\t{e}"
            )

    @staticmethod
    def _check_template_syntax(template: Bunch):
        if isinstance(template, list):
            assert len(template) >= 1, "Template must have at least one element."
            current_type = type(template[0])
            for element in template[1:]:
                assert type(element) == current_type, "Template must be homogeneous."
        elif isinstance(template, dict):
            assert len(template) >= 1, "Template must have at least one element."
            for element in template.values():
                ProjectParser._check_template_syntax(element)

    def check_bombillas(self):
        for experiment in os.listdir("experiments"):
            pass

    def _assert_modules_match(self, template_module, project_module):
        pass

    def _parse_config(self, config: Bunch):
        pass
