<h1 style="color:green"><span style="color:green">Maté 🧉</span></h1>

Maté is a deep learning framework compatible with Pytorch and Tensorflow. It is a package and project manager for deep learning. 
With Maté you can add neural network model dependencies such as ResNet, CNN, RNN, Transformer, and ViT variants to your projects with a simple command line. As a project manager, Maté evaluates, trains, and keeps track of your numerous experiments. Mate adds the source code of the dependencies to your project, making it fully customizable and reprodocible.


### A word of notice
This project is still in its early stages and is not ready for production. Some features are not yet implemented, and some are not yet stable.

## Examples

Please check out the [examples repo](https://github.com/ilex-paraguariensis/examples/).


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
* **Pytorch lightning trainer**

```
    "trainer": {
        "module": "pytorch_lightning",
        "class": "Trainer",
        "params": {
            "gpus": 1,
            "max_epochs": 100,
            "precision": 16,
            "gradient_clip_val": 0.5,
            "enable_checkpointing": true,
            "callbacks": [
                {
                    "module": "pytorch_lightning.callbacks",
                    "class": "EarlyStopping",
                    "params": {
                        "monitor": "val_loss",
                        "patience": 10,
                        "mode": "min"
                    }
                },
                {
                    "module": "pytorch_lightning.callbacks",
                    "class": "ModelCheckpoint",
                    "params": {
                        "dirpath": "{save_dir}/checkpoints",
                        "monitor": "val_loss",
                        "save_top_k": 1,
                        "verbose": true,
                        "save_last": true,
                        "mode": "min"
                    }
                }
            ],
            "logger": {
                "module": "pytorch_lightning.loggers",
                "class": "WandbLogger",
                "params": {
                    "project": "cifar10",
                    "name": "vit_vanilla",
                    "save_dir": "./logs",
                    "log_model": false
                }
            }
        }
    
```


**More tutorials and examples will be added soon!!**


## Is Maté simple to use
A Maté project is just like any other deep learning project with Tensorflow or Pytorch, but the difference is a standard project structure. As of now Maté is a command line tool, and soon Maté commands will be accessible from a web interface. Here are some sample commands that you might need in your experiments:

```
mate add imagen UNet # adds a UNet model with its source code to your project
mate run imagen --input_txt="A Flower in space" # run pretraied model with custom input 
mate train imagen # Takes while to train... 
mate restart imagen # Restart the training
mate snapshot imagen # Reproducible snapshop, keep on experimenting
mate clone imogen exp_imogen # Fork a expriment to keep safe of imogen you have
mate train exp_imogen # Change the code and keep on experimenting!
mate train videoprediction moving_mnist # run videoprediction model with moving_mnist
mate train videoprediction kth # train videoprediction model with kth dataset
```

## What is the Maté standard?
It is a tree structure of foolders and files. It enforces the location of your python files, not what is is inside or how do you define your models, dataloaders or training procedure.

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



## Installation 🔌

At the moment it only works on Linux and MacOS. Windows is on its way.

Install the lastest dev version from git:
```
git clone https://github.com/ilex-paraguariensis/yerbamate -b v2
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

## FAQ
**Q: Does Maté works with colab?**

**A**: Yes! Maté works with colab with little to no effort, in training with colab you need give access to your google drive account and store the dataset and project in your own account.

## Contact 🤝 

For questions please contact:

yerba.mate.dl(at)proton.me
