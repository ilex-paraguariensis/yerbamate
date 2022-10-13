import multiprocessing
import os
import subprocess
import webbrowser


class MateBoard:
    def __init__(self):
        pass

    def start(self):
        # p = multiprocessing.Process(target=self._start)
        # p.start()
        self._start()
        # p.join()

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
            p = subprocess.run(
                "npm start".split(),
                capture_output=True,
                cwd=os.path.join(os.path.dirname(__file__), "mateboard"),
                start_new_session=True,
            )
            stdout = p.stdout


            webbrowser.open("http://localhost:3000")

    def stop(self):
        pass
