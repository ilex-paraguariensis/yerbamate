import multiprocessing
import os
import subprocess
import webbrowser
from typing import Optional


class MateBoard:
    def __init__(self):
        pass

    def start(self):
        # p = multiprocessing.Process(target=self._start)
        # p.start()
        self._start()
        # p.join()
        self._p: Optional[subprocess.Popen] = None

    def _start(self):
        deno_installed = False
        try:
            output = subprocess.check_output("deno -V", shell=True)
            deno_installed = True
        except subprocess.CalledProcessError as grepexc:
            raise Exception(
                "Deno not installed. Please install deno and try again."
            ) from grepexc
        if deno_installed:
            os.system("killall node")
            import ipdb

            ipdb.set_trace()
            self._p = subprocess.run(
                "npm start".split(),
                capture_output=True,
                cwd=os.path.join(os.path.dirname(__file__), "mateboard"),
                start_new_session=True,
            )
            print("You can now open:\n\thttp://localhost:3000")

    def stop(self):
        if self._p:
            self._p.kill()
