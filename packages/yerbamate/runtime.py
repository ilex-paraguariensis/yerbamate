import os
import json
import ipdb


class MateRuntime:
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def save(self):
        with open(self.__runtime_save_path, "w") as f:
            json.dump(self.to_dict(), f)

    def __str__(self):
        return "MateRuntime:" + json.dumps(self.to_dict(), indent=4)

    def __repr__(self):
        return self.__str__()

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
        self.default_checkpoint_location = os.path.join(
            checkpoint_path, "checkpoint.ckpt"
        )
        self.__runtime_save_path = runtime_save_path
