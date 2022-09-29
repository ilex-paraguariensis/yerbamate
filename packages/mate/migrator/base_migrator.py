from abc import ABC, abstractmethod

class Migrator(ABC):

    def __init__(self, config, params):
        self.config = config
        self.params = params

    @abstractmethod
    def migrate(self):
        pass