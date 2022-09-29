import json
import os

from .bunch import Bunch


class Migration:
    def __init__(self, project_root, from_version, to_version):
        self.from_version = from_version
        self.to_version = to_version
        self.name = "Migration"
        self.version = f"{from_version} -> {to_version}"
        self.project_root = project_root

    def __str__(self):
        return f"{self.name} {self.version}"

    def migrate(self):
        if self.from_version == "0.2.4" and self.to_version == "0.2.5":
            self.__migrate_from_0_2_4_to_0_2_5()
        return True

    def __migrate_from_0_2_4_to_0_2_5(self):

        # in this migration, we change hyperparamters to be compatible with the new version of the library

        def migrate_function(params: Bunch):
            if not params.contains("model"):
                return None  # No changes
            models = params.model.keys()
            for model in models:
                params["model"][model]["folder"] = params["model"][model].pop("module")
                params["model"][model]["class"] = params["model"][model].pop("model")
                params["model"][model]["params"] = params["model"][model].pop("params")

            hparams = Bunch(json.loads(json.dumps(params)))
            return hparams

        migrator = BaseParamsMigrator(self.project_root, migrate_function)
        migrator.migrate()
        pass


class BaseParamsMigrator:
    def __init__(self, project_root: str, migrate_func: callable):
        self.migrate_func = migrate_func
        self.root_folder = project_root

    def __list_packages(self, folder: str):
        return (
            tuple(
                x
                for x in os.listdir(os.path.join(self.root_folder, folder))
                if not "__" in x
            )
            if os.path.exists(os.path.join(self.root_folder, folder))
            else tuple()
        )

    def __list_hyperparameters(self, folder: str):
        return (
            tuple(x for x in os.listdir(os.path.join(folder)) if ".json" in x)
            if os.path.exists(os.path.join(folder))
            else tuple()
        )

    def migrate(self):

        models = self.__list_packages("models")
        for model in models:
            hparams_folder = os.path.join(
                self.root_folder, "models", model, "hyperparameters"
            )
            hparams = self.__list_hyperparameters(hparams_folder)
            for hparam_path in hparams:
                hparam = os.path.join(hparams_folder, hparam_path)
                # read the hyperparameter to bunch
                with open(hparam, "r") as f:
                    hparam_bunch = Bunch(json.load(f))
                    # migrate the hyperparameter
                    migrated_params = self.migrate_func(hparam_bunch)

                if migrated_params != None:
                    # write the migrated hyperparameter to the same file
                    with open(hparam, "w") as f:
                        json.dump(migrated_params, f, indent=4)
