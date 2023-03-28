import os

import sys

from time import sleep



from .data.module_repository import ModuleRepository

import ipdb


"""
MATE API

"""


class MateAPI:
    def __init__(self, config):
        # self.config: MateConfig = config
        self.repository = ModuleRepository(config)


    @staticmethod
    def init_project(project_name: str):
        ModuleRepository.init_project(project_name)

    # def generate_metadata(self, rewrite: bool = False):
    #     return self.repository.metadata_generator.generate(rewrite)

    def install_url(self, url: str, *args, **kwargs):
        self.repository.install_url(url, *args, **kwargs)

    def list(self, module: str):
        return self.repository.list(module)
    

    def summary(self):
        return self.repository.get_mate_summary()

    def auto(self, command: str):
        self.repository.auto(command)






