import os
import json


def main():
    print(json.dumps(os.listdir(), indent=4))
    assert os.path.exists("/app/modified.json"), "modified.json not found"
    with open("/app/modified.json", "r") as f:
        modified = json.load(f)
    assert (
        isinstance(modified, list)
        and len(modified) <= 3
        and set(modified) <= {"examples", "yerbamate", "bombilla"}
    )
    os.chdir("/app/yerbamate")
    if not "yerbamate" in modified:
        os.system("git pull")
    if not os.path.exists("dist"):
        os.mkdir("dist")
    os.system("python install.py")
    os.chdir("/app/bombilla")
    if not "bombilla" in modified:
        os.system("git pull")
    os.system("pip install -e .")
    if not "examples" in modified:
        os.chdir("/app/examples/")
        os.system("git pull")
    os.chdir("/app/examples/jax/mnist/mnist")
    os.system("mate train mnist")


if __name__ == "__main__":
    main()
