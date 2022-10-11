import os
import subprocess
import webbrowser

class MateBoard:
    def __init__(self):
        pass

    def start(self):
        deno_installed = False
        try:
            output = subprocess.check_output("deno -V", shell=True)                       
            deno_installed = True
        except subprocess.CalledProcessError as grepexc:                                                                                                   
            raise Exception("Deno not installed. Please install deno and try again.") from grepexc
        if deno_installed:
            subprocess.Popen('npm start'.split(), cwd=os.path.join(os.path.dirname(__file__), "mateboard"))
            webbrowser.open("http://localhost:3000")


    def stop(self):
        pass
