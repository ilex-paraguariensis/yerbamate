# Maté 🧉

## What is Maté?
It is a tool for building research projects in the field of deep learning with [Pytorch](https://pytorch.org/) and builds on top of [Lightning](https://www.pytorchlightning.ai/) and does not intend to replace any of their functionalities. It targets some of the following issues in DL research:

- reproducibility
- replicability
- transparency

It also makes development fast and easy. You can focus more on the model, and less on boilerplate code.

### A word of notice
This project is still at its early stages and is not ready for production. Some features are not yet implemented, and some are not yet stable.


## Is Maté simple to use?
Maté models are nothing but regular torch models. And the training loops are lightning models. Also the default training loops for regression and classification will work for most use-cases so no need to create your own.

Finally, you can change **hyperparameters** by editing a `json` file that looks something like:
```
{
	"batch_size": 32,
	...
}
```

## Installation

At the moment it only works on Linux and MacOS. Windows is on its way. To install mate you need to do the following:
```
git clone https://github.com/ilex-paraguariensis/yerbamate 
cd yerbamate
python install.py
```

## Quick Start
Init a project:
```
mate init my-imagenet-classifier --dataset cifar10 --model resnet
```
And then go ahead and train it!
```
mate train resnet cifar10 
```
The best performing model is saved, along with all of the training hyperparameters, test results, and training logs. In CSV format but also compatible with tensorboard.


If however you want to test a model once again, you can run:
```bash
mate test ResNet
```
This will automatically load the best model and test it.


Install a new model:
```bash
mate install ilex-paraguariensis/UNet
```


Creating *snapshots*. While developing, it is often useful to freeze the current version of a well-perfoming models. And then keep on developing it.
```
mate snapshot ResNet
```
This will create a snapshot of the current model in a separate folder. Keeping track of the version.

## Create your own packages

You can install a model from a git repository:

```
mate install https://gitlab.com/fancyExampleName/fancyModelRepo
````
Or, if the repo is on github, you can use the shorthand notation:

```
mate install ilex-paraguariensis/ResNet
```

## Contact

For questions please contact:

yerba.mate.dl(at)proton.me
