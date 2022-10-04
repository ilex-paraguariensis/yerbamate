from .sources.remote import RemoteDataSource
from .sources.local import LocalDataSource

from .package import Package
from typing import Optional


class PackageManager:
    def __init__(self, root_dir: str = "."):
        self.remote = RemoteDataSource()
        self.local = LocalDataSource(root_dir)

    def get_local_models(self, query: Optional[str] = None):
        return self.local.get_models(query)

    def get_local_trainers(self, query: Optional[str] = None):
        return self.local.get_trainers(query)

    def get_local_data_loaders(self, query: Optional[str] = None):
        return self.local.get_data_loaders(query)

    def get_local_experiments(self, query: Optional[str] = None):
        return self.local.get_experiments(query)
    """
    def query_models(self, query: Optional[str] = None):
        return self.remote.get_models(query)

    def query_trainers(self, query: str = None):
        return self.remote.get_trainers(query)

    def query_datasets(self, query: str = None):
        return self.remote.get_data_loaders(query)

    def install_model(self, model: Package):
        self.local.add_model(model)
    """
