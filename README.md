## Maté 🧉

Maté is a deep learning template project and framework compatible with [PyTorch](https://pytorch.org/) ([Lightning](https://www.pytorchlightning.ai/)), [TensorFlow](https://www.tensorflow.org/) ([Keras](https://keras.io/)), and [Jax](https://github.com/google/jax) ([Flax](https://github.com/google/flax)). Maté is a package and experiment manager for deep learning. 


As a package manager, you can add AI models, trainers/training loops, and data loaders to your projects as dependencies. (coming soon!)


As a project manager, Maté evaluates, trains, and keeps track of your experiments. In addition, Maté adds the source code of the dependencies to your project, making it fully customizable and reproducible.

## Installation 🔌

```bash
pip install yerbamate
```

## Examples

Please check out the [examples repo](https://github.com/ilex-paraguariensis/examples/) for examples of PyTorch Lightning, Keras and Jax.

## Core Principles

- **Modularity**: Divide your project into re-usable/sharable (python) modules.
- **Single Source of Truth**: Maté uses a single JSON configuration file to define an experiment with all the hyperparameters defined there.
- **Don't Get in Developers Way**: Maté tries its best to not get in your way and in fact, you do not have to integrate or import any maté class to your projects. Maté do not enforce any coding style, and only has a loose modular project structure.

## What does Maté offer?

- **Reproducibility**: Out-of-the-box Maté projects are fully reproducible. You can share your project with anyone and they can run the same experiments as you did.
- **Reusability and Shareability**: Maté offers reusability/shareability of any modules (e.g., trainers, models and data loaders) between Maté projets.
- **Customizability**: Maté is fully compatible with any framework. For example in case you use pytorch-lightning, out of the box you can use W&B, Tensorboard, or any other pytorch-lightning logger.


### What is the Maté standard?

Maté enforces modularity and separation of three essential components of a deep learning project:

- models,
- trainers (optional),
- data loaders

Each model, data loader, and trainer must be a python module inside its folder.
This guarantees out-of-the-box sharing of models, data loaders, and trainers between Maté projects.

This is how folders in a 🧉 project are organized:

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

## Comparison to familiar tools

- *Weights & Biases* wandb is a logger and allows model weights sharing as well
- *Tensorboard* This is a logger and can be integrated into mate
- *[Monai](https://github.com/Project-MONAI/MONAI)*
- *[Ivy](https://github.com/unifyai/ivy)*
- *[THINGSvision](https://github.com/ViCCo-Group/thingsvision)*


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

---

**Q: But I like wandb! Does this try to replac it?**

**A**: No! 🧉 supports wandb. Just just choose it as a logger.

## Test with Docker

```bash
cd docker
bash run-test.sh
```

## Contact 🤝 

- yerba.maté.dl(at)proton.me
- [@mate_dl](https://twitter.com/mate_dl)

