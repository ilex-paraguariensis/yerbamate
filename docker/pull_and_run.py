import os

os.chdir("/app/yerbamate")
os.system("git pull")
os.system("pip install -e .")

os.chdir("/app/yerbamate")
os.system("git pull --recurse-submodules")
os.system("python install.py")

os.chdir("/app/examples")
os.system("git pull")

os.chdir("/app/examples/jax/mnist/mnist")
print(os.listdir())
os.system("mate train mnist")
