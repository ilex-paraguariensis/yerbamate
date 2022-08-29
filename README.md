<h1 style="color:green"><span style="color:green">Maté 🧉</span></h1>
## What is Maté?
Maté is a deep learning framework built upon Pytorch(and soon Tensorflow). It is a package and project manager for deep learning projects. 
With Maté you can add neural network dependencies such as CNN, RNN, Transformer, and ViT variants to your projects with a simple command line. As a project manager, Maté trains, evaluates models and keep tracks of your numerous experiments. Mate adds the source code of the dependencies to your project, making it fully customizable.


### A word of notice
This project is still in its early stages and is not ready for production. Some features are not yet implemented, and some are not yet stable.

## HelloMatéWorld
Maté reads a `mate.json` configuration filw and runs the experiment. In this file you can select tasks, models, optimizers, and datasets e.g.,
```
{
	"batch_size": 32,
	"task" : "classification",
	"optimizer":...	
	"transformer":..,
	"resnet":"...
	...
}
```



## Is Maté simple to use

```
mate run imagen --input_txt="A Flower in space"
mate train imagen # Tooks while... and doesnt stops training if you do not have a stopper.
mate restart imagen 
mate snapshot imagen # reproducible snapshop, keep on experimenting
mate clone imogen exp_imogen # fork a expriment, to keep safe of imogen you have
mate train exp_imogen 
```


## Installation 🔌

At the moment it only works on Linux and MacOS. Windows is on its way.
To install the stable version of mate you need to do the following:
```
pip install yerbamate
```

To install the latest development version:
```
git clone https://github.com/ilex-paraguariensis/yerbamate 
cd yerbamate
python install.py
```

## Quick Start 🔥
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

## FAQ
**Q: Does Maté works with colab?**

**A**: Yes! Maté works with colab with little to no effort, in training with colab you need give access to your google drive account and store the dataset and project in your own account.

## Contact 🤝 

For questions please contact:

yerba.mate.dl(at)proton.me
