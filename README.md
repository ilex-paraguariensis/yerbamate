<h1 style="color:green"><span style="color:green">Maté 🧉</span></h1>

Welcome to Maté - the versatile and efficient deep learning framework! Maté is a package and experiment manager that seamlessly integrates with popular deep learning libraries such as PyTorch, TensorFlow, and JAX. Whether you are a seasoned deep learning researcher or just starting out, Maté provides you with the tools to easily add models, trainers, and data loaders to your projects. With Maté, you can also evaluate, train, and keep track of your experiments with ease. By including the source code of dependencies directly in your project, Maté ensures full customizability and reproducibility of your results. Get started with Maté today and elevate your deep learning experience! 🚀

## Installation 🔌

```bash
pip install yerbamate
```



## Examples 📚

Please check out the [transfer learning](https://github.com/oalee/big-transfer), [vision models](https://github.com/oalee/deep-vision),
and [lightweight gan](https://github.com/oalee/lightweight-gan).

## Quick Start ⚡

**Initialize a project**

```bash
mate init my_project
```

**List all modules(trainers/data/models/experiments)**

```bash
mate list 
```

**Train a model**

```bash
mate train experiment my_experiment
# or alternatively use python
python -m train my_project.experiment.my_experiment
```

**Install a module**

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



**Clone a model**

```bash
mate clone resnet my_resnet
```


## Documentation 📚


### Modularity
Modularity is a software design principle that focuses on creating self-contained, reusable and interchangeable components. In the context of a deep learning project, modularity means creating standalone modules that can perform specific functions such as data loading, model training, or evaluation. This allows for a more organized, maintainable and scalable project structure. 
### Project Structure
Maté enforces a project structure that is modular and easy to navigate. The project structure is shown below:
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
All independent sub modules (meaning they don't import from each other) should be placed in their respective folders. For example, a model should be placed in the models folder, a trainer should be placed in the trainers folder, and a data loader should be placed in the data folder. This allows for out-of-the-box sharing of models, data loaders, and trainers.


### Experiment Definition
An experiment is a combination of a model, trainer, and data loader. An experiment is defined in the experiments module. 

### Maté Environment
The Maté Environment API is a tool for managing your environment variables. It offers a convenient way to set, retrieve and manage these variables throughout your project. The API first searches for an env.json file to find the environment variables, and if it doesn't find one, it then looks to the operating system's environment variables. With the Maté Environment API, you can easily store and access environment-specific information such as API keys, database URLs, and more, ensuring that your application runs smoothly no matter the environment.

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
    "results": "/home/user/results",
  
}
```

or in the operating system's environment variables:
```bash
export data=/home/user/data
export results=/home/user/results
```

The action (train/test/etc) is automatically set by the CLI and can be accessed in the environment variable:
```
mate {train/test/etc} experiment my_experiment
python -m my_project.experiment.my_experiment {train/test/etc}
```



<!-- Please check out the [documentation](https://yerba-mate.readthedocs.io/en/latest/). -->

## FAQ
**Q: Does Maté work with colab?**

**A**: Yes! Maté works with colab as any Maté project is exportable to a juypter notebook.

## Contact 🤝 

For questions please contact:

yerba.mate.dl(at)proton.me
