import os
import json
from collections import OrderedDict

def main():
    dockerfile = """
    FROM archlinux:latest
    RUN pacman -Syu --noconfirm
    RUN pacman -S python python-pip deno git --noconfirm
    RUN pip install numpy jax jaxlib torch torchvision ipdb regex validators setuptools wheel
    WORKDIR /app
    COPY ./__run__.py /app/run.py
    # CMD ["ls", "-lah", "/app"]
    """.strip("\t")
    end = """CMD ["python", "run.py"]\n"""
    modules:OrderedDict[str, str] = OrderedDict(
        yerbamate="git clone --recurse-submodules https://github.com/ilex-paraguariensis/yerbamate -b v2",
        bombilla="git clone https://github.com/ilex-paraguariensis/bombilla",
        examples="git clone https://github.com/ilex-paraguariensis/examples"
    )

    os.system("docker build -t mate-test .")
    folders = os.listdir("dev")
    assert set(folders) <= set(modules.keys())
    with open("modified.json", "w") as f:
        f.write(json.dumps(folders))
    for key in modules:
        """
        print(f"Mounting folder {path} in the container")
        mount = f'-v "$(pwd)"/{path}:/app/{folder}'
        mounts.append(mount)
        # os.system(f"docker cp {os.path.join('dev', folder)} mate-test:/app/{folder}")
        """
        if key in folders:
            dockerfile += f"COPY ./dev/{key} /app/{key}\n"
        else:
            dockerfile += f"RUN {modules[key]}\n"
    if len(folders) == 0:
        print("Testing latest version of all modules.")
    dockerfile += "COPY modified.json /app/modified.json\n"
    dockerfile += end
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)
    exec_str = f"docker run -it --rm mate-test --name mate-test"
    print(exec_str)
    os.system(exec_str)


if __name__ == "__main__":
    main()
