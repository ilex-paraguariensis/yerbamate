import os

os.system("python rm -r dist")
os.system("python setup.py sdist")

file = os.listdir("dist")[0]

os.system(f"pip install dist/{file} --force-reinstall")
