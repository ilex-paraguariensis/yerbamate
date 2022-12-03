import os
import json
import ipdb


class MateRuntime:
    def save(self):
        data = {k: v for k, v in self.__dict__.items() if not k.startswith("__")}
        with open(self.__runtime_save_path, "w") as f:
            json.dump(data, f)

    def __init__(
        self,
        *,
        command: str,
        save_dir: str,
        checkpoint_path: str,
        runtime_save_path: str
    ):
        self.command = command
        self.checkpoint_path = checkpoint_path
        self.save_dir = save_dir
        self.default_checkpoint_location = os.path.join(checkpoint_path, "checkpoint.ckpt")
        self.__runtime_save_path = runtime_save_path
