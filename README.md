# Mate 🧉

## What is Mate?
It is a tool for building research projects in the field of deep learning with pytorch.
It makes development fast, easy, and the results replicable. You can focus more on the model, and less on boilerplate code.

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

## Example Folder Structure
```
├── classification-demo
│   ├── base_lightning
│   │   └── BaseClassificationLightningModule.py
│   ├── data
│   │   ├── cifar10
│   │   │   ├── data_loader.py
│   │   │   └── parameters.json
│   │   └── imagenet
│   │       ├── data_loader.py
│   │       ├── parameters.json
│   │       └── pre_processing.py
│   ├── env_parameters.json
│   ├── models
│   │   ├── convlstm
│   │   │   ├── convlstmcell
│   │   │   │   ├── convlstmcell.py
│   │   │   │   └── parameters.json
│   │   │   ├── convlstm.py
│   │   │   ├── model.py
│   │   │   └── parameters.json
│   │   └── resnet
│   │       ├── model.py
│   │       ├── parameters.json
│   │       └── resnet.py
│   ├── parameters.json
│   └── snapshots
│       └── resnet__1
│           ├── model.py
│           ├── parameters.json
│           └── resnet.py
├── mate.json
└── README.md
```

## Create your own packages

You can install a model from a git repository:
```
mate install https://gitlab.com/fancyExampleName/fancyModelRepo
````
Or, if the repo is on github, you can use the shorthand notation:
```
mate install ilex-paraguariensis/ResNet
```

