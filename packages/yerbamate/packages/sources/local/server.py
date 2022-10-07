from .local import LocalDataSource
from flask import Flask
import ipdb
from threading import Thread


class LocalServer:
    def __init__(self, local_ds: LocalDataSource) -> None:
        self.local_ds = local_ds

        # run server in a thread

        t = Thread(target=self.run_server)
        t.start()

    def run_server(self):
        app = Flask(__name__)

        @app.route("/list")
        def list(query=None):
            return self.local_ds.list(query)

        @app.route("/experiment")
        def experiment(experiment: str):
            exp, _ = self.local_ds.load_experiment(experiment)
            return exp

        @app.route("/experiments")
        def experiments():
            return self.local_ds.get_all_experiments()

        app.run(port=3001)
