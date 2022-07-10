# used for migrating hyperparameters

from mate.migrator.base_migrator import Migrator


class ParamsMigrator(Migrator):

    def __init__(self, config, params):
        super().__init__(config, params)

    def added_default_new_params(self):
        pass

    def migrate(self):
        pass
