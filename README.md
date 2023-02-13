<h1 style="color:green"><span style="color:green">Maté 🧉</span> your modular AI project and experiment manager</h1>

Maté is a python project, package and experiment manager. Whether you are a
seasoned deep learning researcher or just starting out, Maté provides you with
the tools to easily add source code and dependencies of models, trainers, and
data loaders to your projects. With Maté, you can also evaluate, train, and keep
track of your experiments with ease 🚀

## Features 🎉

- Seamless integration with any python library such as PyTorch/Lightning,
  TensorFlow/Keras, JAX/Flax, Huggingface/transformers.
- Easy to use interface to add source code of models, trainers, and data loaders
  to your projects.
- Support for full customizability and reproducibility of results through the
  inclusion of dependencies in your project.
- Modular project structure that enforces a clean and organized codebase.
- Fully compatible with python. No need to use mate commands to run your
  experiments. 
- Convenient environment management through the Maté Environment API.
- Support for pip and conda for dependency management.
- Works with Colab.

## Table of Contents

- [Installation](#installation-🔌)
- [Quick Start](#quick-start-⚡)
- [Project Structure](#project-structure-📁)
- [Example Projects](#example-projects-📚)
- [Documentation](https://oalee.github.io/yerbamate/)
- [Contribution](#Contribution-🤝)

## Installation 🔌

```bash
pip install yerbamate
```

## Quick Start ⚡

### **Initialize a project**

```bash
mate init deepnet
```

This will generate the following empty project structure:

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

To install an experiment, you can use `mate install` to install a module and its
dependencies from a github repository. See
[docs](https://oalee.github.io/yerbamate/#/?id=install) for more details.

```bash
# Short version of GitHub URL https://github.com/oalee/big_transfer/tree/master/big_transfer/experiments/bit
mate install oalee/big_transfer/experiments/bit -yo pip

# Short version of GitHub URL https://github.com/oalee/deep-vision/tree/main/deepnet/experiments/resnet
mate install oalee/deep-vision/deepnet/experiments/resnet -yo pip
```

### **Install a module**

You can install independant modules such as models, trainers, and data loaders
from github projects that follow the
[Independent modular project structure](https://oalee.github.io/yerbamate/#/?id=project-structure-%f0%9f%93%81).

```bash
mate install oalee/lightweight-gan/lgan/trainers/lgan 
mate install oalee/big_transfer/models/bit -yo pip
mate install oalee/deep-vision/deepnet/models/vit_pytorch -yo pip
mate install oalee/deep-vision/deepnet/trainers/classification -yo pip
```

### **Setting up environment**

Take a look at
[Environment API](https://oalee.github.io/yerbamate#maté-environment-api) and
set up your environment before running your experiments.

### **Train a model**

To train a model, you can use the `mate train` command. This command will train
the model with the specified experiment. For example, to train the an experiment
called `learn` in the `bit` module, you can use the following command:

```bash
mate train bit learn
# or alternatively use python
python -m deepnet.experiments.bit.learn train
```

## Project Structure 📁

Deep learning projects can be organized into the following structure with
modularity and seperation of concerns in mind. This offers a clean and organized
codebase that is easy to maintain and is sharable out-of-the-box.

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

### Sample Modular Project Structure

This structure highlights modularity and seperation of concerns. The `models`,
`data` and `trainers` modules are independent and can be used in any project.
The `experiments` module is not independent, but rather combines the three
modules together to create a complete experiment.

```bash
.
├── mate.json
└── deepnet
    ├── data
    │   ├── bit
    │   │   ├── fewshot.py
    │   │   ├── __init__.py
    │   │   ├── minibatch_fewshot.py
    │   │   ├── requirements.txt
    │   │   └── transforms.py
    │   └── __init__.py
    ├── experiments
    │   ├── bit
    │   │   ├── aug.py
    │   │   ├── dependencies.json
    │   │   ├── __init__.py
    │   │   ├── learn.py
    │   │   └── requirements.txt
    │   └── __init__.py
    ├── __init__.py
    ├── models
    │   ├── bit_torch
    │   │   ├── downloader
    │   │   │   ├── downloader.py
    │   │   │   ├── __init__.py
    │   │   │   ├── requirements.txt
    │   │   │   └── utils.py
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   └── requirements.txt
    │   └── __init__.py
    └── trainers
        ├── bit_torch
        │   ├── __init__.py
        │   ├── lbtoolbox.py
        │   ├── logger.py
        │   ├── lr_schduler.py
        │   ├── requirements.txt
        │   └── trainer.py
        └── __init__.py
```

## Example Projects 📚

Please check out the [transfer learning](https://github.com/oalee/big_transfer),
[vision models](https://github.com/oalee/deep-vision), and
[lightweight gan](https://github.com/oalee/lightweight-gan).

## Documentation 📚

Please check out the [documentation](https://oalee.github.io/yerbamate).

## Guides 📖

For more information on modularity, please check out this [guide](https://medium.com/@alee.rmi/the-ultimate-deep-learning-project-structure-a-software-engineers-guide-into-the-land-of-ai-c383f234fd2f).

For running experiments on Google Colab, please check out this
[example](https://colab.research.google.com/gist/oalee/5f5c2b3bb2da4ec3168f3edd4a52056a/deep-learning.ipynb)

## Contribution 🤝

We welcome contributions from the community! Please check out our
[contributing](https://github.com/oalee/yerbamate/blob/main/CONTRIBUTING.md)
guide for more information on how to get started.

## Contact 🤝

For questions please contact:

oalee(at)proton.me
