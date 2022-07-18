# Maté 🧉

## What is Mate?
It is a tool for building research projects in the field of deep learning with [Pytorch](https://pytorch.org/) and builds on top of [Lightning](https://www.pytorchlightning.ai/) and does not intend to replace any of their functionalities.
It makes development fast, easy, and the results replicable. You can focus more on the model, and less on boilerplate code.


### A word of notice
This project is still at its early stages and is not ready for production. Some features are not yet implemented, and some are not yet stable.

## Installation

To install mate you need to do the following:
```
git clone https://github.com/ilex-paraguariensis/yerbamate 
cd yerbamate
python install.py
```

## Quick Start
Install a model:
```bash
mate install ilex-paraguariensis/ResNet
```
Then train it:
```bash
mate train ResNet
```
The best performing model is saved, along with all of the training hyperparameters, test results, and training logs.

If however you want to test a model once again, you can run:
```bash
mate test ResNet
```
Creating *snapshots*. While developing, it is often useful to freeze the current version of a well-perfoming models. And then keep on developing it.
```
mate snapshot ResNet # will create a snapshot of the current model in a separate folder
```
## Create your own packages
```
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
