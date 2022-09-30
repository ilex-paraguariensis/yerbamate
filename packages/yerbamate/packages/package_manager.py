from .sources.remote import RemoteDataSource
from .sources.local import LocalDataSource

from .package import Package


class PackageManager:
    def __init__(self):
        self.remote = RemoteDataSource()
        self.local = LocalDataSource()

    def locally_available_models(self):
        return self.local.get_models()

    def locally_available_trainers(self):
        return self.local.get_trainers()

    def locally_available_packages(self):
        return self.local.get_packages()

    def query_models(self, query: str = None):
        return self.remote.get_models(query)

    def query_trainers(self, query: str = None):
        return self.remote.get_trainers(query)

    def query_datasets(self, query: str = None):
        return self.remote.get_datasets(query)

    def install_model(self, model: Package):
        self.local.add_model(model)
