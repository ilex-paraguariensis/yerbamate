import os
from .mate_api import MateAPI
from typing import Optional
from rich import print


class Mate:
    def __init__(self):
        self.current_folder = os.path.dirname(__file__)
        self.api = MateAPI()
        # self.models = self.__list_packages("models")
        self.is_restart = False
        self.run_params = None

    @staticmethod
    def init(project_name: str):
        MateAPI.init(project_name)

    def remove(self, target: str):
        self.api.remove(target)

    def show(self, path: str):
        self.api.show(path)

    def summary(self):
        # self.api.summary()
        # print(self.api)
        print(self.api.to_tree())

    def results(self):
        results_table = self.api.results()
        if results_table is not None:
            print(results_table)
        else:
            print("No results found.")

    def list(
        self, module_name: str, query: Optional[str] = None, output_json: bool = True
    ):
        print(self.api.project[module_name])

    def clone(self, source_model: str, target_model: str):
        self.api.clone(source_model, target_model)

    def create(self, path: str, name: str):
        self.api.create(path, name)

    def snapshot(self, model_name: str):
        pass

    def train(self, experiment_name: str = "default"):
        self.api.train(experiment_name=experiment_name)

    def rename(self, path: str, name: str):
        self.api.rename(path, name)

    def export(self, source: str):
        self.api.export(source)

    def metadata(
        self,
    ):
        self.api.generate_metadata(True)

    def test(self, experiment_name: str):
        self.api.test(experiment_name)

    def restart(self, model_name: str, params: str = "default"):
        """
        TODO: Implement restart in trainer
        """
        pass
        # assert io.experiment_exists(
        #    self.root_folder, model_name, params
        # ), f'Model "{model_name}" does not exist.'
        # io.assert_experiment_exists(self.root_folder, model_name, params)

        # self.is_restart = True
        # self.__fit(model_name, params)

    def tune(self, model: str, params: tuple[str, ...]):
        """
        Fine tunes specified hyperparameters. (Not implemented yet)
        """
        pass

    def generate(self, model_name: str, params: str):
        pass

    def sample(self, model_name: str, params: str):
        pass

    def install(self, url: str):
        """
        Adds a dependency to a model.
        """
        self.api.install(url)

    def exec(self, model: str, params: str, exec_file: str):
        params = "parameters" if params == "" or params == "None" else params
        print(f"Executing model {model} with result of: {params}")
        _, model, _ = self.__get_trainer(model, params)

        self.__load_exec_function(exec_file)(model)

    def board(self):

        self.api.start_mateboard()

    # def __list_packages(self, folder: str):
    #     return io.list_packages(self.root_folder, folder)

    # def __update_mate_version(self):
    #     utils.migrate_mate_version(self.config, self.root_folder)

    # def __findroot(self):
    #     """
    #     Method in charge of finding the root folder of the project and reading the content of mate.json
    #     """
    #     self.root_save_folder = self.config.results_folder
