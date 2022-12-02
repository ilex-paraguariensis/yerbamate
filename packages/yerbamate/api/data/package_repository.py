from distutils.command.config import config
import threading
from sympy import re
from yerbamate.api.data.metadata.metadata import Metadata
from yerbamate.api.data.package_manager import PackageManager
from yerbamate.mate_config import MateConfig
from .sources.remote import RemoteDataSource
from .sources.local.local import LocalDataSource
from .sources.local.server import LocalServer
from pipreqs import pipreqs

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
        # self.metadata_generator = MetadataGenerator(
        #     config.project, config.metadata, self.local
        # )
        # if run_local_api_server:
        #     self.local_server = LocalServer(self.metadata_generator, self.local)
        #
        # TODO: we should refresh the metadata every time we run a command
        # self.generate_metadata()
        self.metadata: Optional[dict] = None

    def install_url(self, url: str):
        self.package_manager.install_package(url)

    def generate_metadata(self, rewrite: bool = False):

        self.__generate_metadata()

        base_meta = self.config.metadata.base_metadata()
        base_meta["exports"] = self.__export_metadata()
        base_meta["dependencies"] = self.__generate_pip_requirements()
        base_meta["experiments"] = self.local.list("experiments")
        # self.config.metadata = base_meta
        self.config.save()

    def __export_metadata(self):
        assert self.metadata is not None, "Metadata shuldn't be None"
        meta = self.metadata

        exports = {k: {} for k in meta.keys()}
        for key, value in meta.items():
            if type(value) == dict:
                for key2, value2 in value.items():
                    if type(value2) == dict:
                        if "url" in value2:
                            exports[key][key2] = value2["url"]
                            continue
                        else:
                            for key3, value3 in value2.items():
                                if type(value3) == dict:
                                    if "url" in value3:
                                        if key2 not in exports[key]:
                                            exports[key][key2] = {}

                                        exports[key][key2][key3] = value3["url"]
                                        continue

        return exports

    def __generate_pip_requirements(self):

        imports = pipreqs.get_all_imports(self.config.project)
        # import_info_remote = pipreqs.get_imports_info(imports)
        import_info_local = pipreqs.get_import_local(imports)

        import_info = []

        for im in import_info_local:

            name = im["name"]
            version = im["version"]

            res = {
                "name": name,
                "version": version,
            }

            # for remote in import_info_remote:
            #     if remote["name"] == name:
            #         lastVersion = remote["version"]
            #         res["last_version"] = lastVersion

            import_info.append(res)

        return {"pip": import_info}

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
