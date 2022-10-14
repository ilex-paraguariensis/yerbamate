from yerbamate.mate_config import MateConfig
from .sources.remote import RemoteDataSource
from .sources.local.local import LocalDataSource
from .sources.local.server import LocalServer

from .package import Package
from typing import Optional
import ipdb
from .metadata.generator import MetadataGenerator


class PackageRepository:
    def __init__(self, config: MateConfig, run_local_api_server: bool = False):
        self.config = config
        self.remote = RemoteDataSource()
        self.local = LocalDataSource(config)
        self.metadata_generator = MetadataGenerator(
            config.project, config.metadata, self.local
        )
        if run_local_api_server:
            self.local_server = LocalServer(self.metadata_generator, self.local)

        self.metadata_generator.generate()

    # def list(self, module: str, query: Optional[str] = None):
    #     print(self.local.list(module, query))
    def list(self, module: str, query: Optional[str] = None):
        return self.local.list(module, query)

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
