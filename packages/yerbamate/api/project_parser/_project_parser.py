import json
import os
from typing import Union, Optional

JSON = Union[dict, list, str, int, float]


class JSONChecker:
    def __init__(
        self, *, json_template_file_name: Optional[str], json_template: Optional[JSON]
    ):
        if json_template_file_name:
            with open(json_template_file_name, "r") as json_template_file:
                self.json_template = json.load(json_template_file)
        elif json_template:
            self.json_template = json_template

    def check_from_file_name(self, json_file_name: str):
        with open(json_file_name, "r") as json_file:
            json_data = json.load(json_file)
        self.__check(json_data, self.json_template)

    def check_from_JSON(self, json_data: JSON):
        self.__check(json_data, self.json_template)

    def __check(self, json_data: JSON, json_template: JSON):
        if isinstance(json_data, dict):
            for key in json_template:
                assert key in json_data, "{} not in {}".format(key, json_data)
                if type(json_template[key]) == dict:
                    self.__check(json_data[key], json_template[key])
                elif type(json_template[key]) == list:
                    self.__check_list(json_data[key], json_template[key])
                assert type(json_template[key]) == type(
                    json_data[key]
                ), "{} is not {}".format(json_data[key], type(json_template[key]))
        elif isinstance(json_data, list):
            self.__check_list(json_data, json_template)
        else:
            assert type(json_template) == type(json_data), "{} is not {}".format(
                json_data, type(json_template)
            )

    def __check_list(self, json_data: list, json_template: list):
        for item, template in zip(json_data, json_template):
            self.__check(item, template)


class DirectoryChecker:
    def __init__(self, template_directory_name: str):
        self.template_directory_name = template_directory_name

    def directory_to_json(self, directory_name: str) -> JSON:
        # reads all sub-folders and files in the directory and generates a json file that represents it
        result = {directory_name: {}}
        for root, dirs, files in os.walk(directory_name):
            elements = dirs + files
            destination_dict = result
            for element in root.split(os.sep)[1:]:
                if element not in destination_dict:
                    destination_dict[element] = {}
                destination_dict = destination_dict[element]
            for element in elements:
                if element not in destination_dict:
                    destination_dict[element] = {}
                destination_dict = destination_dict[element]
        return result

    def __call__(self, directory_name: str):
        template_json = self.directory_to_json(self.template_directory_name)
        data_json = self.directory_to_json(directory_name)
        checker = JSONChecker(template_json)
        checker.check_from_JSON(data_json)


class ProjectParser:
    def __init__(self, project_path: str):
        pass
