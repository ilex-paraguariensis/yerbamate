import threading
from yerbamate.api.data.package_manager import PackageManager
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
        self.package_manager = PackageManager(config)
        self.remote = RemoteDataSource()
        self.local = LocalDataSource(config)
        self.metadata_generator = MetadataGenerator(
            config.project, config.metadata, self.local
        )
        if run_local_api_server:
            self.local_server = LocalServer(self.metadata_generator, self.local)

        # TODO: we should refresh the metadata every time we run a command
        self.generate_metadata()
        self.metadata: Optional[dict] = None

    def install_url(self, url: str):
        self.package_manager.install_package(url)

    def generate_metadata(self):
        # run in paralle
        th = threading.Thread(target=self.__generate_metadata, args=())
        th.start()

        th.join()
        # we need to wait for the metadata to be generated, race condition with bombilla generating return types

    def __generate_metadata(self):
        self.metadata = self.metadata_generator.generate()

    # def list(self, module: str, query: Optional[str] = None):
    #     print(self.local.list(module, query))
    def list(self, module: str, query: Optional[str] = None):
        return self.local.list(module, query)

    def get_mate_summary(self):
        if self.metadata is None:
            self.__generate_metadata()
        assert self.metadata is not None, "Metadata shuldn't be None"
        summary = {key: val for key, val in self.metadata.items()}
        summary["experiments"] = self.local.get_all_experiments()
        return summary

    def install_package(self, package: Package):
        self.local.install_package(package)

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
