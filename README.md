## Maté 🧉

Maté is a deep learning template project and framework compatible with [PyTorch](https://pytorch.org/) ([lightning](https://www.pytorchlightning.ai/)), [TensorFlow](https://www.tensorflow.org/) ([Keras](https://keras.io/)), and [Jax](https://github.com/google/jax) ([Flax](https://github.com/google/flax)). It is a package and experiment manager for deep learning. 


As a package manager, you can add AI models, trainers/training loops, and data loaders to your projects as dependencies.


As a project manager, Maté evaluates, trains, and keeps track of your experiments. In addition, Maté adds the source code of the dependencies to your project, making it fully customizable and reproducible.

## Installation 🔌

```bash
pip install yerbamate
```

## Examples

Please check out the [examples repo](https://github.com/ilex-paraguariensis/examples/) for examples of PyTorch Lightning, Keras and Jax.

## Core Principles

- **Modularity**: Divide your project into sharable (python) modules.
- **Reproducibility**: Through just one (JSON) file you can reproduce an entire experiment all all its hyperparameters
- Maté🧉 is intuitive and flexible: no need to add boilerplate code, just take it away!

### What is the Maté standard?
Maté enforces **modularity** and seperation of three basic components of a deep learning project:

- models,
- trainers(optional),
- data loaders

Each model, data loader and trainer should be a module inside its respective folder. This allows for out-of-the-box sharing of models, data loaders, and trainers between Maté projects. 

An example of a the foolder structure of a maté project is shown below:

```
├── root_project_folder
│   ├── data
│   │   ├── __init__.py
│   │   ├── cifar
│   │   │   ├── __init__.py
│   │   │   ├── cifar10.py
|
│   ├── models
│   │   ├── __init__.py
│   │   ├── resnet
│   │   │   ├── __init__.py
│   │   │   ├── resnet.py
|
│   ├── trainers
│   │   ├── __init__.py
│   │   ├── classifier
│   │   │   ├── __init__.py
│   │   │   ├── classifier.py
|
│   ├── experiments
│   │   ├── resnet18_cifar10.json
│   │   ├── resnet34_cifar10.json

```



### For Coders
Dear coders, we try our best to not get in your way and in fact, you do not have to integrate or import any maté class to your projects. Maté simply parses the configuration. To make your project maté compatible, you need to move a few files and make a Bombilla configuration file. 

### Maté configuration (AKA [Bombilla](https://github.com/ilex-paraguariensis/bombilla)🧉)
Maté defines an experiment with a configuration file, aka [Bombilla](https://github.com/ilex-paraguariensis/bombilla), that is a ordered dictionary describing arguments and python objects in plain json. [Bombilla](https://github.com/ilex-paraguariensis/bombilla) supports any python module; including all the local project level modules and installed py packages (eg., tensorflow, pytorch, x_transformers, torchvision, vit_pytorch). 


## Quick Start ⚡

**Run an experiment/train your model**

```bash
maté train my_experiment
```

**Evaluate a model**

```bash
maté test my_experiment
```

**Run a model**

```bash
maté run feature_extraction my_experiment
```

**Clone a model**

```bash
maté clone resnet my_resnet
```

**More tutorials, features and examples will be added soon!!**


## FAQ
**Q: Does Maté work with colab?**

**A**: Yes! Maté works with colab as any Maté project is exportable to a juypter notebook.

## Contact 🤝 


- yerba.maté.dl(at)proton.me
- [@mate_dl](https://twitter.com/mate_dl)

