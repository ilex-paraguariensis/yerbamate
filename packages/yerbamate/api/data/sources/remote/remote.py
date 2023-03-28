from ..source import DataSource


# TODO: this class should call API to get the data
class RemoteDataSource(DataSource):
    def __init__(self):
        super().__init__()
        self.models = []
        self.trainers = []
        self.datasets = []
        self.experiments = []
        self.packages = []

    def get_models(self, query: str = None):
        return self.models

    def get_trainers(self, query: str = None):
        return self.trainers

    def get_data_loaders(self, query: str = None):
        return self.datasets

    def get_experiments(self, query: str = None):
        return self.experiments

    def get_packages(self, query: str = None):
        return self.packages

    def add_model(self, model):
        self.models.append(model)

    def add_trainer(self, trainer):
        self.trainers.append(trainer)

    def add_dataset(self, dataset):
        self.datasets.append(dataset)

    def add_experiment(self, experiment):
        self.experiments.append(experiment)

    def add_package(self, package):
        self.packages.append(package)
