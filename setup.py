from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name="yerbamate",
    description=" A python module and experiment manager for deep learning",
    author="Giulio Zani, Ali Rahimi",
    author_email="yerba.mate.dl@proton.me",
    url="https://github.com/oalee/yerbamate",
    python_requires=">=3.6",
    version="0.9.24",
    packages=find_packages("packages", exclude=["tests"]),
    include_package_data=True,
    package_dir={"": "packages/"},
    license="Apache License 2.0",
    license_files=("LICENSE",),
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        "colorama",
        "GitPython",
        "validators",
        "ipdb",
        "pipreqs",
        "dirhash",
        "rich",
        "docstring-parser",
        "tabulate"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3"
    ],
    scripts=["./src/mate"],
)
