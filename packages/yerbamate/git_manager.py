import os
import ipdb
import json


class GitManager:
    @staticmethod
    def from_url(mate_root: str, full_url: str):
        """Parse a full URL and return a GitManager object"""
        tree_split = full_url.split("tree/")
        repo = tree_split[0]
        repo_name = repo.split("/")[3]
        # extracts the branch name from the URL
        branch = tree_split[1].split("/")[0]
        # extracts the commit hash from the URL
        path = "/".join(tree_split[1].split("/")[2:])
        # extracts the tree hash from the URL
        return GitManager(
            mate_root=mate_root,
            repo_name=repo_name,
            repo=repo,
            branch=branch,
            path=path,
        )

    def __init__(
        self, *, mate_root: str, repo_name: str, repo: str, branch: str, path: str
    ):
        self.mate_root = mate_root
        self.repo: str = repo
        self.repo_name: str = repo_name
        self.branch: str = branch
        self.path: str = path

    def __look_for_mate(self, path: str):
        """Look recursively for mate.json inside the cloned repository"""
        for root, dirs, files in os.walk(path):
            if "mate.json" in files:
                return os.path.join(root, "mate.json")
            else:
                for d in dirs:
                    if self.__look_for_mate(os.path.join(root, d)) is not None:
                        return self.__look_for_mate(os.path.join(root, d))
        return None

    def __name_to_id(self, name: str):
        return name.replace(" ", "_").replace("-", "_").lower()

    def clone(self, tmp_destination: str, destination: str | None = None):
        """Clone the repository"""
        if os.path.exists(tmp_destination):
            os.system(f"rm -rf {tmp_destination}")
        os.system(f"git clone {self.repo} -b {self.branch} {tmp_destination}")
        # look for mate.json inside the cloned repository
        mate_path = self.__look_for_mate(tmp_destination)
        if mate_path is None:
            raise Exception("mate.json not found")
        mate_root = os.path.dirname(mate_path)
        if destination is None:
            destination = os.path.join(self.mate_root, self.path)
            if os.path.exists(destination):
                new_id = self.__name_to_id(self.repo_name) + "_"
                split_path = self.path.split("/")
                destination = os.path.join(
                    self.mate_root,
                    *split_path[:-1],
                    new_id + split_path[-1],
                )
                print(f"Destination already exists, created: {destination}")
        command = f"mv {os.path.join(mate_root, self.path)} {destination}"
        os.system(command)
        os.system(f"rm -rf {tmp_destination}/*")

    def __str__(self):
        inner = "\n".join(
            ["\t" + key + "=" + str(val) for key, val in self.__dict__.items()]
        )
        return f"GitManager(\n{inner}\n)"


if __name__ == "__main__":
    # test
    git_manager = GitManager.from_url(
        "https://github.com/ilex-paraguariensis/jax-inception-resnet-densenet/tree/main/tutorial5/data/loaders/cifar10"
    )
    git_manager.clone("./tmp", "./tmp2/destination")
