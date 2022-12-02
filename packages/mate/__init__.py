import json as __json
import os as __os

command: str = ""
is_train: bool = False
is_test: bool = False
is_restart: bool = False


def __main():
    dir_name = __os.getcwd()
    runtime_filename = __os.path.join(dir_name, ".mate", "runtime.json")
    with open(runtime_filename, "r") as f:
        __runtime = __json.load(f)
    for key, val in __runtime.items():
        globals()[key] = val

__main()
if command == "train":
    is_train = True
elif command == "test":
    is_test = True
elif command == "restart":
    is_restart = True


