<h1 style="color:green"><a href="https://github.com/oalee/yerbamate"><span style="color:green">Maté</span></a>🧉 your friendly AI project and experiment manager</h1>

[Maté](https://github.com/oalee/yerbamate)🧉 is a python project, package and experiment manager. Whether you are a
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
- [Module Installation](#module-installation-📦)
- [Maté Environment API](#maté-environment-api)
- [Experiment Definition](#experiment-definition)
- [Command Line Interface](#command-line-interface-📝)

## Installation 🔌

```bash
pip install yerbamate
```

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

To install an experiment, you can use `mate install` to install a module and its
dependencies from a github repository. See [Install](#install) for more details.

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

### **List all modules**

List all your models, trainers, data and experiments modules:

```bash
mate list
```

### **Setting up environment**

Take a look at [Environment API](#maté-environment-api) and set up your
environment before running your experiments.

### **Train a model**

To train a model, you can use the `mate train` command. This command will train
the model with the specified experiment. For example, to train the an experiment
called `learn` in the `bit` module, you can use the following command:

```bash
mate train bit learn
# or alternatively use python
python -m train deepnet.experiments.bit.learn
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

### Example Project Structure

```bash
.
├── deepcnn
│   ├── data
│   │   ├── cifar10
│   │   │   ├── data_loader.py
│   │   │   ├── __init__.py
│   │   │   └── requirements.txt
│   │   └── __init__.py
│   ├── experiments
│   │   ├── __init__.py
│   │   └── resnet
│   │       ├── cifar_10_resnet_fine_tune.py
│   │       ├── cifar_10_resnet.py
│   │       ├── dependencies.json
│   │       ├── __init__.py
│   │       ├── requirements.txt
│   │       ├── tune_clean.py
│   │       └── tune.py
│   ├── __init__.py
│   ├── models
│   │   ├── __init__.py
│   │   └── resnet
│   │       ├── __init__.py
│   │       ├── requirements.txt
│   │       └── resnet
│   │           ├── COPYRIGHT
│   │           ├── fine_tune.py
│   │           ├── __init__.py
│   │           ├── LICENSE
│   │           ├── requirements.txt
│   │           └── resnet.py
│   └── trainers
│       ├── classification
│       │   ├── __init__.py
│       │   ├── pl_classification.py
│       │   └── requirements.txt
│       └── __init__.py
└── mate.json

11 directories, 27 files
```

## Example Projects 📚

Please check out the [transfer learning](https://github.com/oalee/big_transfer),
[vision models](https://github.com/oalee/deep-vision), and
[lightweight gan](https://github.com/oalee/lightweight-gan).

## Module Installation 📦

Maté supports the installation of code modules from github repositories.

### **Install a module**

To install a module, you can use `mate install` to install a module from a
github repository. All modules inside a project that follow modularity can be
independently installed.

```bash
mate install https://github.com/oalee/big_transfer/tree/master/big_transfer/experiments/bit
```

This will install the big transfer experiment into your project. You can also
use the shorthand version of the command:

```bash
mate install oalee/big_transfer/experiments/bit
```

### **Install dependencies**

Maté supports both pip and conda for dependency management when
`requirements.txt` and `dependencies.json` are exported (see
[Export](export-a-module)). To install dependencies, you can use `mate install`
with the `-y {option}` flag to install dependencies. Options include `pip` and
`conda`. The -o flag will overwrite the code dependencies if it already exists.
For example, to install the big transfer experiment with pip dependencies, you
can use the following command:

```bash
mate install oalee/big_transfer/experiments/bit -yo pip
mate install oalee/big_transfer/experiments/bit -yo conda
```

### **Install python module**

To install a python module, you can use `mate install` to install a module from
a github repo with the full path to the module. This way, you can install any
python module into your project. For example, to install the pytorch image
module, you can use the following command:

```bash
mate install https://github.com/rwightman/pytorch-image-models/tree/main/timm
```

The module will be installed into your project, However python module
dependencies will not be installed. To install the python module dependencies,
you can use either manually install the dependencies or simply use
`pip install module` to make sure dependencies are installed.

### **Export a module**

To export, share your modules (models/trainers/data/experiments) you can use the
following command, then push and share the module with others:

```bash
mate export
```

This command will generate `requirements.txt`, `dependencies.json` and `export.md` for
sharing, dependency management and reprodiciblity.

### **Examples**

```bash
# Installs the experiment, code and python dependencies with pip
mate install oalee/big_transfer/experiments/bit -y pip

# Installs python dependencies with conda
# Overwrites code dependencies if it already exists
mate install oalee/big_transfer/experiments/bit -yo conda

# Only installs the code without any pip/conda dependencies
mate install oalee/big_transfer/experiments/bit -n

# installs a fine tuning resnet experiment
mate install https://github.com/oalee/deep-vision/tree/main/deepnet/experiments/resnet

# Short install version of this repo: https://github.com/oalee/deep-vision
# installs a customizable pytorch resnet model implementation
mate install oalee/deep-vision/deepnet/models/resnet

# installs cifar10 data loader for pytorch lightning
mate install oalee/deep-vision/deepnet/data/cifar10

# installs augmentation module seperated from torch image models
mate install oalee/deep-vision/deepnet/data/torch_aug

# installs over 30 Vision in Transformers implementations into models
mate install oalee/deep-vision/deepnet/models/torch_vit

# Or install torch_vit from lucidrains as a non independent module
mate install https://github.com/lucidrains/vit-pytorch/tree/main/vit_pytorch

# installs a pytorch lightning classifier module
mate install oalee/deep-vision/deepnet/trainers/pl_classification

# installs pytorch lightning gan training module from lightweight-gan repo
mate install oalee/lightweight-gan/lgan/trainers/lgan
```

## Maté Environment API

The Maté Environment API is a tool for managing your environment variables. It
offers a convenient way to set, retrieve and manage these variables throughout
your project. The API first searches for an env.json file to find the
environment variables, and if it doesn't find one, it then looks to the
operating system's environment variables. With the Maté Environment API, you can
easily store and access environment-specific information such as API keys,
database URLs, and more, ensuring that your application runs smoothly no matter
the environment.

You can access the Maté Environment API in your experiments:

```python
import yerbamate

env = yerbamate.Environment()

env.name # Automatically assigns the name of the experiment as "experiment_module.exp_name"
env.results # Automatically appends "experiment_module/exp_name" to the results directory passed from environment variables


# access environment variables
data_dir = env["data"]
results = env["results]

if env.train:
    # do something
else env.test:
    # do something else
```

The environment variables can be set in the env.json file:

```json
{
  "data": "/home/user/data",
  "results": "/home/user/results"
}
```

or in the operating system's environment variables:

```bash
export data=/home/user/data
export results=/home/user/results
```

The action (train/test/etc) in `env.{action}` is automatically set to `True`
from the CLI command and can be accessed in the environment variable:

```
mate {train/test/etc} experiment my_experiment
python -m my_project.experiment.my_experiment {train/test/etc}
```

## Experiment Definition

Maté uses python to define hyperparameters of an experiment. An experiment is a
combination of a model, trainer, and data loader and is defined in the
experiments module.

```python
from ...data.cifar10 import CifarLightningDataModule
from ...trainers.classification import LightningClassificationModule
from ...models.resnet import ResNetTuneModel
from torchvision.models import resnet18, resnet34
import sys, os, torch, pytorch_lightning as pl, yerbamate 

env = yerbamate.Environment()
network = ResNetTuneModel(
    resnet34(pretrained=True), num_classes=10, update_all_params=True
)
optimizer = torch.optim.Adam(network.parameters(), lr=0.0004, betas=[0.9, 0.999])
lr_scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer,
    mode="min",
    factor=0.5,
    patience=2,
    verbose=True,
    threshold=1e-06,
)
optimizer = {
    "optimizer": optimizer,
    "lr_scheduler": lr_scheduler,
    "monitor": "val_loss",
}

pl_module = LightningClassificationModule(network, optimizer)
data_module = CifarLightningDataModule(env["DATA_PATH"], batch_size=128, image_size=[32, 32])
logger = pl.loggers.TensorBoardLogger(env["logs"], env.name) 
callbacks = [
    pl.callbacks.ModelCheckpoint(
        monitor="val_accuracy",
        save_top_k=1,
        mode="max",
        dirpath= env["results"],
        save_last=True,
    ),
    pl.callbacks.EarlyStopping(monitor="val_loss", patience=10, mode="min"),
]
pl_trainer = pl.Trainer(
    accelerator="gpu",
    max_epochs=100,
    logger=logger,
    callbacks=callbacks,
    precision=16,
    gradient_clip_val=0.5,
)
if env.train:
    pl_trainer.fit(pl_module, data_module)
if env.restart:
    pl_trainer.fit(
        pl_module, data_module, ckpt_path=os.path.join( env["results"], "last.ckpt")
    )
elif env.test: 
    pl_trainer.test(pl_module, data_module, ckpt_path=os.path.join( env["results"], "last.ckpt"))
```

## Command line interface 📝

Mate provides a command line interface to manage your projects. The following
commands are available:


 --- 


### `mate` auto


`mate auto {command}`

Various commands to help with the development process.


commands:
- `export`: Creates a requirements.txt and dependencies.json files for sharing and reproducibility.
- `init`: Automatically creates `__init__.py` files in the project structure.

Example:


    mate auto export
    mate auto init

 --- 

### `mate` clone

`mate clone {module} {name} {dest} {-o}`

Clones a source code module to a new destination.

Args:

    module: Module to clone.

    name: Name of the module to clone.

    dest: Destination to clone the module to.

    -o: Overwrite destination if it exists.

Example:

`mate clone models torch_vit my_vit`

 --- 

### `mate` export

Generates requirements.txt, dependencies.json and exports.md for sharing and reproducibility.

Example:
`mate export`

Output:
```
Generated requirements.txt for gan/models/lgan
Generated dependencies.json for gan/experiments/lwgan
Generated requirements.txt for gan/experiments/lwgan
Generated requirements.txt for gan/trainers/lgan
Generated requirements.txt for gan/data/cars
Exported to export.md
```


 --- 

### `mate` init


`mate init {project_name}`

Initializes a new project.
This will create the following structure:
```
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

Args:
    
    project_name: Name of the project.

Example:

    mate init my_project


 --- 

### `mate` install

Intalls a module from a git repository.

Usage: ``mate install {url} {-y|n|o} {pm}``

Install module support the following formats:
- ``mate install {complete_url}``
- ``mate install {user}/{repo}/{root_module}/{module}``
- ``mate install {user}/{repo|root_module}/{module}``

Args:

    url: Url of the git repository.
    -y: Skips confirmation and installs python dependencies
    -n: Skips installing python dependencies
    -o: Overwrites existing code modules
    pm: Package manager to use. Defaults to asking the user.


Example Installing a module from structured git repository (recommended):


    mate install oalee/deep-vision/deepnet/models/torch_vit -yo pip

    This will install the module `torch_vit` from the repository `oalee/deep-vision` in to your `models` folder.
    The `yo` flags will skip confirmation and install python dependencies using pip.

Example Installing a module from unstructured git repository:


    mate install https://github.com/rwightman/pytorch-image-models/tree/main/timm


    This will install the module `timm` from the repository as a sister module to your root module.
    Take into account that this will install only the code and not the python dependencies.

 --- 

### `mate` list



Lists all available modules.

Args:
    module_name: Name of the module to list. If not specified, all modules will be listed.

Examples:
    mate list models

    mate list


 --- 

### `mate` summary

Prints a summary of the project modules. Same as `mate list`

 --- 

### `mate` test

Executes an experiment.

Usage: ``mate test {module} {experiment}``

Args:

    exp_module: Name of the module where the experiment is located.

    exp: Name of the experiment.

Example:
    `
    mate test experiments my_experiment`

This will run the experiment `my_experiment` located in the `experiments` module.

Equivalent to `python -m root_module.experiments.my_experiment test`

 --- 

### `mate` train

Executes an experiment.

Usage: ``mate train {module} {experiment}``

Args:

    exp_module: Name of the module where the experiment is located.

    exp: Name of the experiment.

Example:
    `
    mate train experiments my_experiment`

This will run the experiment `my_experiment` located in the `experiments` module.

Equivalent to `python -m root_module.experiments.my_experiment train`

 --- 


## Guides 📖

For more information on modularity, please check out this
[guide](https://medium.com/@alee.rmi/the-ultimate-deep-learning-project-structure-a-software-engineers-guide-into-the-land-of-ai-c383f234fd2f).

For running experiments on Google Colab, please check out this
[example](https://colab.research.google.com/gist/oalee/5f5c2b3bb2da4ec3168f3edd4a52056a/deep-learning.ipynb)

## Contributing 🤝

We welcome contributions from the community! Please check out our
[contributing](https://github.com/oalee/yerbamate/blob/main/CONTRIBUTING.md)
guide for more information on how to get started.

## Contact 🤝

For questions please contact:

oalee(at)proton.me