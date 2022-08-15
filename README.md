<h1 style="color:green"><span style="color:green">Maté 🧉</span></h1>

## What is Maté?
Maté is a deep learning framework built upon Pytorch and soon Tensorflow. It serves as a package and project manager for deep learning projects. With Maté you can add neural network dependencies such as  ResNet or ViT variants to your projects with a simple command line. As a project manager, Maté provides easy to use functionalities for training, evaluating, and experimenting with various architectures on different datasets while preserving results of your experiments. 


Maté targets some of the following issues in DL research:

- reproducibility
- replicability
- transparency

It also makes development fast and easy. It helps you to focus on the model, and less on boilerplate code.

### A word of notice
This project is still at its early stages and is not ready for production. Some features are not yet implemented, and some are not yet stable.


## Is Maté simple to use?
Maté models are nothing but regular torch models. And the training loops are lightning models. Also the default training loops for regression and classification will work for most use-cases so no need to create your own.

Finally, you can change **hyperparameters** by editing a `json` file that looks something like the following: ([click here for a detailed example](https://github.com/ilex-paraguariensis/yerbamate/wiki/Sample-Hyperparameter))
```
{
	"batch_size": 32,
	"optimizer":...
	"transformer":...
	...
}
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

**A**: Yes! Maté works with colab with little to no effort, in training with colab you need give access to your google drive account and store the dataset and project in your google drive account.

## Contact 🤝 

For questions please contact:

yerba.mate.dl(at)proton.me
