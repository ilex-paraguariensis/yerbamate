import json as __json
import os as __os

command: str = ""
is_train: bool = False
is_test: bool = False
is_restart: bool = False
checkpoint_path: str = ""
default_checkpoint_location = ""
save_dir: str = ""


def __main():
    dir_name = __os.getcwd()
    runtime_filename = __os.path.join(dir_name, ".mate", "runtime.json")
    with open(runtime_filename, "r") as f:
        __runtime = __json.load(f)
    for key, val in __runtime.items():
        assert key in globals(), f"Key '{key}' not found in globals"
        globals()[key] = val


__main()

is_train = command == "train"
is_test = command == "test"
is_restart = command == "restart"


def result(values: dict[str, float | int]):
    result_path = __os.path.join(save_dir, "result.json")
    result = {}
    if __os.path.exists(result_path):
        with open(result_path, "r") as f:
            result = __json.load(f)
    result = result | values
    with open(result_path, "w") as f:
        __json.dump(result, f)
    print(f"Result: {__json.dumps(result, indent=4)}")
    print(f"Result saved to {result_path}")
