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
    description="A cowsay clone for python in one file.",
    author="Giulio Zani, Ali Rahimi",
    author_email="yerba.mate.dl@proton.me",
    url="https://github.com/ilex-paraguariensis/yerbamate",
    python_requires=">=3.9",
    version="0.8.10",
    packages=find_packages("packages", exclude=["tests"]),
    include_package_data=True,
    package_dir={"": "packages/"},
    license="Apache License 2.0",
    license_files=("LICENSE.md",),
    install_requires=["bomba"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    scripts=["./src/mate"],
)
