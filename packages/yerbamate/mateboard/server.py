import json
import multiprocessing
import os
import queue
import sys
import threading
from time import sleep
from yerbamate.api.data.sources.local import io
from yerbamate.mate_config import MateConfig
from yerbamate.mateboard.mateboard import MateBoard
from yerbamate.trainers.trainer import Trainer
from yerbamate.utils.bunch import Bunch

from ..api.data.package_repository import PackageRepository

from typing import Optional, Union
import ipdb


import asyncio
import websocket
import websockets
from ..api.socket import WebSocketServer

"""
Mate Internal Server API

"""

import subprocess


class InternalServer:
    def __init__(self):

        self.__findroot()
        assert self.config is not None, "Mate.json not found"

        self.repository = PackageRepository(self.config, True)
        self.exp: Optional[Bunch] = None
        self.exp_name: Optional[str] = None
        self.save_dir: Optional[str] = None
        self.checkpoint_path: Optional[str] = None
        self.trainer: Optional[Trainer] = None

        self.ws = WebSocketServer(on_train_request=self.train_request)

        self.mateboard = self.start_mateboard()

    def __findroot(self):
        """
        Method in charge of finding the root folder of the project and reading the content of mate.json
        """
        self.root_folder, self.config = io.find_root()
        self.root_save_folder = self.config.results_folder

    def start_mateboard(self):

        board = MateBoard()
        board.start()
        return board

    def train_request(self, request: dict):
        # run on the main loop

        if request["type"] == "start_training":
            print("start_training")
            cmd = f"mate train {request['experiment_id']}"
            cwd = os.getcwd()
            print("cmd cwd", cmd, cwd)
            th = multiprocessing.Process(target=self._run_process, args=(cmd, cwd))
            th.start()
            print("process", th)

        # print("select experiment", experiment_name)
        # self.select_experiment(experiment_name)

    def _run_process(self, cmd: str, cwd: str):
        process = subprocess.run(
            cmd.split(" "),
            cwd=cwd,
            start_new_session=True,
        )
        # self.stream_pipe(process.stdout

        # os.system(cmd)
        print("process", process)

    def stream_pipe(self, p):

        # another process is reading this pipe, so we need to read it in a loop
        while True:
            inline = p.stdout.readline()
            if not inline:
                break
            sys.stdout.write(inline)
            sys.stdout.flush()


def run():
    server = InternalServer()
    print("Starting Mateboard")
