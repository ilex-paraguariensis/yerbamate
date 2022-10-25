from yerbamate.mate_config import MateConfig
from ..sources.local import LocalDataSource

from .metadata import BaseMetadata, Metadata
from bombilla import Bombilla
from bombilla.node import Node, load_node


class ExperimentMetadataGenerator(object):
    """Generates experiment metadata.

    This class is responsible for generating experiment metadata for a given
    experiment. It is used by the generator to generate the metadata for the
    whole project.

    Attributes:
        experiment (str): The name of the experiment.
        root_meta (BaseMetadata): The root metadata of the project.
        local_ds (LocalDataSource): The local data source.
    """

    def __init__(
        self,
        experiment: str,
        root_module: str,
        root_meta: Metadata,
        local_ds: LocalDataSource,
    ) -> None:
        """Initializes the experiment metadata generator.

        Args:
            experiment (str): The name of the experiment.
            root_module (str): The root module of the project.
            root_meta (Metadata): The root metadata of the project.
            local_ds (LocalDataSource): The local data source.
        """
        self.experiment = experiment
        self.root_meta = root_meta
        self.local_ds = local_ds
        Node._root_module = root_module

    def generate(self, rewrite: bool = True) -> dict:
        """Generates the experiment metadata.

        Args:
            rewrite (bool, optional): Whether to rewrite the metadata. Defaults to True.

        Returns:
            dict: The experiment metadata.
        """
        experiment, _ = self.local_ds.load_experiment(f"{self.experiment}")
        experiment = dict(experiment)

        node = load_node(experiment)
        node.__load__()

        full_experiment = node.generate_full_dict()
        base_meta = self.root_meta.base_metadata()

        result = {
            **base_meta,
            "experiment_name": self.experiment,
            "experiment": full_experiment,
        }

        if rewrite:
            self.local_ds.save_experiment(result, f"{self.experiment}.metadata")

        return result
