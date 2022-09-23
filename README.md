<h1 style="color:green"><span style="color:green">Maté 🧉</span></h1>

Maté is a deep learning framework compatible with Pytorch and Tensorflow. It is a package and project manager for deep learning. With Maté, a simple command can add neural network model dependencies such as ResNet, CNN, RNN, Transformer, and ViT variants to your projects. As a project manager, Maté evaluates, trains, and keeps track of your experiments. In addition, mate adds the source code of the dependencies to your project, making it fully customizable and reproducible.

### A word of notice
This project is still in its early stages and is not ready for production. Some features are not yet implemented, and some are not yet stable.



## Is Maté simple to use?
A Maté project is just like any other deep learning project with Tensorflow or Pytorch, but the difference is a standard project structure. As of now Maté is a command line tool, and soon the standard Maté graphical user interface will be ready, check out (MatéBoard)[https://github.com/ilex-paraguariensis/mateboard].



## Installation 🔌

At the moment it only works on Linux and MacOS. Windows is on its way.
<!--
Install the stable version via pip:

```
pip install yerbamate
```
-->
Install the lastest dev version from git:
```
git clone https://github.com/ilex-paraguariensis/yerbamate 
cd yerbamate
python install.py
```

## Quick Start ⚡
Create a new project:
```
mate init my-imagenet-classifier --dataset cifar10 --model resnet
```
And then go ahead and train it (no coding so far 🤗).
```
mate train resnet cifar10 
```
The best performing model is saved, along with all of the training hyperparameters, test results, and training logs. In CSV format but also compatible with tensorboard.

Adding dependencies:
```
mate add myvideoprediction ViT CrossFormer CvT
```


If however you want to test a model once again, you can run:
```bash
mate test resnet
```
This will automatically load the best model and test it.


Install a new model:
```bash
mate install ilex-paraguariensis/UNet
```


While developing, it's handy to freeze a *snapshot* the current version of a well-perfoming models. And then keep on developing it.
```
mate snapshot ResNet
```
This will create a snapshot of the current model in a separate folder. Keeping track of the version.

## Publish your models 🎁 
If you are using mate in a public repo, then anyone can install your models in their own mate project.


To install a model from a git repository:
```
mate install https://gitlab.com/fancyExampleName/fancyModelRepo
````
Or, if the repo is on github, you can use the shorthand notation:

```
mate install ilex-paraguariensis/ResNet 
```

## What is the Maté standard?
It is a tree structure of folders and files. It enforces the location of your python files, not what is inside or how do you define your models, dataloaders or training procedure.

The root folder contrains the follwing folders: 
* Models
* Data
* Executables

Inside the Models folder have your experiments, e.g.,
* ResNet
* ResNetBig
* YetABiggerResNet
* ViT

Inside the `Model` folder, you would need to have the source of of the models and trainers.

Inside the `Data` folder, you would have your dataloaders, augmentation and preprocessings.

The `Excetuables` can be used to run a trained model. 

## For Coders (Developers, Researchers, and Engineers)
Dear coders, we try our best to not get in your way and in fact, you do not have to integrate or import any mate class to your projects. Mate simply parses the configuration. To make your project mate compatible, you need to make a Mate configuration file. Mate works with torch and keras out of the box. Now, you might want to know: what is this configuration?!

### Mate configuration (AKA Bombilla 🧉)
Mate defines an experiment with a configuration file, aka Bombilla, that is a ordered dictionary describing arguments and python objects in plain json. Bombilla supports any python module; including all the local project level modules and installed py packages (eg., tensorflow, pytorch, x_transformers, torchvision, vit_pytorch). Mate generates objects in a Bombilla with DFS search. 

**Note that all the arguments are directly passed to the object constructor, so you can use any argument that is accepted by the fucntion call. For example, in the below example, we can select any logger and pass any parameters as long as they are accepted by the object constructor.**

Here you can see some examples of objects in Bombilla format:
* custom neural network that fine tunes a pretrained resnet:
```
            "classifier": {
                "module": "modules.resnet.fine_tune",
                "class": "ResNetTuneModel",
                "object_key": "classifier",
                "params": {
                    "num_classes": 10,
                    "resnet": {
                        "module": "torchvision.models",
                        "class": "resnet18",
                        "params": {
                            "pretrained": true
                        }
                    }
                }
            },


```


## FAQ
**Q: Does Maté work with colab?**

**A**: Yes! Maté works with colab as any Maté project is exportable to a juypter notebook.

## Contact 🤝 

For questions please contact:

yerba.mate.dl(at)proton.me
