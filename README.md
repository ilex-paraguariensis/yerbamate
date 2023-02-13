<h1 style="color:green"><span style="color:green">Maté 🧉</span> - AI Project and Experiment Manager</h1>

Maté is a python AI project, package and experiment manager. Whether you are a
seasoned deep learning researcher or just starting out, Maté provides you with
the tools to easily add source code and dependencies of models, trainers, and
data loaders to your projects. With Maté, you can also evaluate, train, and keep
track of your experiments with ease. By including the source code of
dependencies directly in your project. Maté ensures full customizability and
reproducibility of your results. Get started with Maté today and elevate your
deep learning experience! 🚀

## Features 🎉
* Seamless integration with popular deep learning libraries such as PyTorch, TensorFlow, and JAX.
* Easy to use interface to add source code of models, trainers, and data loaders to your projects.
* Support for full customizability and reproducibility of results through the inclusion of source code dependencies in your project.
* Modular project structure that enforces a clean and organized codebase.
* Convenient environment management through the Maté Environment API.
* Support for pip and conda for dependency management.
* Works with Colab.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Example Projects](#example-projects)
- [Documentation](#documentation) 
- [Contributing](#contributing) 
- [FAQ](#faq) 



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

To install an experiment, you can use `mate install` to install a module from a github repository:

```bash
mate install oalee/big_transfer/experiments/bit -yo pip
```

### **List all modules**

List all your models, trainers, data and experiments modules:

```bash
mate list
```

### **Train a model**

To train a model, you can use the `mate train` command. This command will train
the model with the specified experiment. For example, to train the an experiment
called `learn` in the `bit` module, you can use the following command:

```bash
mate train bit learn
# or alternatively use python
python -m train deepnet.experiments.bit.learn
```

### **Export a module**

To export, share your modules (models/trainers/data/experiments) you can use the
following command, then push and share the module with others:

```bash
mate export
```

This command will generate `requirements.txt` and `dependencies.json` for
sharing, dependency management and reprodiciblity.

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

Maté supports both pip and conda for dependency management. To install
dependencies, you can use `mate install` with the `-y {option}` flag to install
dependencies. Options include `pip` and `conda`. The -o flag will overwrite the
code dependencies if it already exists. For example, to install the big transfer
experiment with pip dependencies, you can use the following command:

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

### **Clone a model**

```bash
mate clone resnet my_resnet
```

## Example Projects 📚

Please check out the [transfer learning](https://github.com/oalee/big-transfer),
[vision models](https://github.com/oalee/deep-vision), and
[lightweight gan](https://github.com/oalee/lightweight-gan).

## Documentation 📚

### Modularity

Modularity is a software design principle that focuses on creating
self-contained, reusable and interchangeable components. In the context of a
deep learning project, modularity means creating three independent standalone
modules for models, trainers and data. This allows for a more organized,
maintainable and scalable project structure. The forth module, experiments, is
not independent, but rather combines the three modules together to create a
complete experiment.

### Project Structure

Maté enforces a project structure that is modular and easy to navigate. The
project structure is shown below:

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

All independent sub modules (meaning they don't import from each other) should
be placed in their respective folders. For example, a model should be placed in
the models folder, a trainer should be placed in the trainers folder, and a data
loader should be placed in the data folder. This allows for out-of-the-box
sharing of models, data loaders, and trainers.

### Maté Environment

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

### Experiment Definition

An experiment is a combination of a model, trainer, and data loader. An
experiment is defined in the experiments module.

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

<!-- Please check out the [documentation](https://yerba-mate.readthedocs.io/en/latest/). -->




## Contributing 🤝

We welcome contributions from the community! Please check out our
[contributing](https://github.com/oalee/yerbamate/blob/main/CONTRIBUTING.md)
guide for more information on how to get started.


## Contact 🤝

For questions please contact:

yerba.mate.dl(at)proton.me
