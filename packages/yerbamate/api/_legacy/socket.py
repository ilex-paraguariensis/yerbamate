import asyncio
from asyncio import subprocess
import json
import multiprocessing
import threading
from time import sleep
from traitlets import Callable
import websocket
import websockets
import threading
import ipdb
import queue


class WebSocketServer:
    def __init__(self, port: int = 8765, on_train_request: Callable = None):

        self.on_train_request = on_train_request
        self.ws = websockets.serve(self.serve, "localhost", port)
        self.active_connections = []

        self.ws_thread = threading.Thread(target=self.run_server)
        self.ws_thread.start()
        # self.ws_thread.start()

    def run_server(self):
        print("run_server")
        asyncio.run(self.main())
        print("run_server")

    def send_message(self, message):
        print("send_message")

        # asyncio.run(self._send_message(message))

    async def serve(self, websocket):

        self.active_connections.append([websocket])

        async for message in websocket:
            print("Message received", message)
            response = self.parse_request(message)
            await websocket.send(json.dumps(response))

    async def main(self):
        async with websockets.serve(self.serve, "localhost", 8765):
            await asyncio.Future()  # run forever

    async def _send_message(self, message):
        # return
        if type(message) == dict:
            message = json.dumps(message)

        for connection in self.active_connections:
            await connection.send(message)
            # asyncio.run_coroutine_threadsafe(
            #     conn.send(message), asyncio.get_event_loop()
            # )

    def handle_train_request(self, request):
        print("handle_train_request")
        # run on the main loop
        # print("train request", request)
        self.on_train_request(request)

        # self.from_dummy_thread(lambda: self.on_train_request(request))

        # self.from_main_thread_blocking()

    def parse_request(self, request):

        # try to parse the request as json
        try:
            print("Parsing request as json")
            request = json.loads(request)

            if "type" in request:
                print("Request type found")
                if request["type"] == "start_training":
                    print("Request type is start_training")
                    exp_name = request["experiment_id"]
                    print(f"Request experiment_id is {exp_name}")
                    # th = threading.Thread(target=self.handle_train_request, args=(exp_name,))
                    self.handle_train_request(request)
                    print("Request sent to on_train_request")
                    return json.dumps({"state": "training"})

                if request["type"] == "stop_training":
                    return json.dumps({"state": "stopping"})

            return json.dumps(request)
        except:
            return request
