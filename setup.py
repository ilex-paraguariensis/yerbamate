from setuptools import setup, find_packages

"""
setup(
    name="yerbamate",
    version="0.3.2",
    license="MIT",
    author="Giulio Zani, Ali Rahimi",
    author_email="giulio.zani@gmail.com",
    scripts=["src/run.py"],
    packages=["src/yerbamate", "mate"],
    url="https://github.com/giuliozani/mate",
    keywords="deep_learning machine_learning package_manager",
    install_requires=["torch", "pytorch_lightning", "numpy",],
)
"""
setup(
    name="yerbamate",
    description=" A python module and experiment manager for deep learning",
    author="Giulio Zani, Ali Rahimi",
    author_email="yerba.mate.dl@proton.me",
    url="https://github.com/oalee/yerbamate",
    python_requires=">=3.9",
    version="0.9.13",
    packages=find_packages("packages", exclude=["tests"]),
    include_package_data=True,
    package_dir={"": "packages/"},
    license="Apache License 2.0",
    license_files=("LICENSE",),
    install_requires=[
        "ipdb",
        "pipreqs",
        "dirhash",
        "docstring-parser",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3"
    ],
    scripts=["./src/mate", "./src/mateboard"],
)
