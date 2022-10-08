from .local import LocalDataSource
from flask import Flask
import ipdb
from threading import Thread
from flask import request, jsonify
from flask_cors import CORS
import json
from ...metadata.generator import MetadataGenerator


class LocalServer:
    def __init__(self, generator: MetadataGenerator, local_ds: LocalDataSource) -> None:
        self.local_ds = local_ds
        self.metadata = generator.generate()
        # print(self.metadata)
        # run server in a thread
        t = Thread(target=self.run_server)
        t.start()

    def run_server(self):
        app = Flask(__name__)
        CORS(app)
        @app.route("/list_<query>")
        def list(query):
            # query = request.args["query"]
            # return self.local_ds.list(query)
            if query != "experiments":
                return jsonify(self.metadata[query])
            else:
                return jsonify(self.local_ds.list(query))


        @app.route("/experiment_<experiment>")
        def experiment(experiment: str):
            exp, _ = self.local_ds.load_experiment(experiment)
            return exp

        @app.route("/experiments")
        def experiments():
            return self.local_ds.get_all_experiments()

        @app.route("/update_experiment_<experiment_name>", methods=["POST"])
        def update_experiment(experiment_name: str):
            json_str = json.loads(request.data)
            # TODO: update experiment
            return "ok"

        app.route("/train_<experiment_name>")

        def train(experiment):
            # TODO: tell websocket to stop experiment
            pass

        def stop():
            # TOSO: tell websocket to stop
            pass

        app.run(port=3001)
