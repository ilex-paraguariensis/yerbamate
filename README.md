<h1 style="color:green"><span style="color:green">Maté 🧉</span>, your friendly AI project and experiment manager</h1>

Maté is a python project, package and experiment manager. Whether you are a
seasoned deep learning researcher or just starting out, Maté provides you with
the tools to easily add source code and dependencies of models, trainers, and
data loaders to your projects. With Maté, you can also evaluate, train, and keep
track of your experiments with ease 🚀

## Features 🎉

- Seamless integration with popular deep learning libraries such as PyTorch,
  TensorFlow, and JAX.
- Easy to use interface to add source code of models, trainers, and data loaders
  to your projects.
- Support for full customizability and reproducibility of results through the
  inclusion of source code dependencies in your project.
- Modular project structure that enforces a clean and organized codebase.
- Convenient environment management through the Maté Environment API.
- Support for pip and conda for dependency management.
- Works with Colab.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Example Projects](#example-projects)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [FAQ](#faq)

## Installation 🔌

```bash
pip install yerbamate
```

## Project Structure 📁

Maté projects are organized into the following structure with modularity in
mind. This offers a clean and organized codebase that is easy to maintain and is
sharable out-of-the-box.

```bash
/
|-- models/
|   |-- __init__.py
|-- experiments/
|   |-- __init__.py
|-- trainers/
|   |-- __init__.py
|-- data/
|   |-- __init__.py
```

### Modularity

Modularity is a software design principle that focuses on creating
self-contained, reusable and interchangeable components. In the context of a
deep learning project, modularity means creating three independent standalone
modules for models, trainers and data. This allows for a more organized,
maintainable and sharable project structure. The forth module, experiments, is
not independent, but rather combines the three modules together to create a
complete experiment.

## Quick Start ⚡

### **Initialize a project**

```bash
mate init deepnet
```

This will generate the following structure:

```bash
/
|-- models/
|   |-- __init__.py
|-- experiments/
|   |-- __init__.py
|-- trainers/
|   |-- __init__.py
|-- data/
|   |-- __init__.py
```

### **Install an experiment**

To install an experiment, you can use `mate install` to install a module from a
github repository:

```bash
mate install oalee/big_transfer/experiments/bit -yo pip
```

### **Setting up environment**
Take a look at [Environment API](https://oalee.github.io/yerbamate#maté-environment-api) and set up your environment before running your experiments.

### **Train a model**

To train a model, you can use the `mate train` command. This command will train
the model with the specified experiment. For example, to train the an experiment
called `learn` in the `bit` module, you can use the following command:

```bash
mate train bit learn
# or alternatively use python
python -m train deepnet.experiments.bit.learn
```


## Example Projects 📚

Please check out the [transfer learning](https://github.com/oalee/big-transfer),
[vision models](https://github.com/oalee/deep-vision), and
[lightweight gan](https://github.com/oalee/lightweight-gan).


## Documentation 📚
Please check out the [documentation](https://oalee.github.io/yerbamate).

## Guides 📖

For more information on modularity, please check out this [guide]().

## Contributing 🤝

We welcome contributions from the community! Please check out our
[contributing](https://github.com/oalee/yerbamate/blob/main/CONTRIBUTING.md)
guide for more information on how to get started.

## Contact 🤝

For questions please contact:

yerba.mate.dl(at)proton.me
