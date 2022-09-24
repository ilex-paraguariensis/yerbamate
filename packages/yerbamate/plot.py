import os
import pandas as pd
import ipdb
import torch as t
import matplotlib.pyplot as plt


def plot(path: str):
    val_file = os.path.join(path, "val_performance.csv")
    train_file = os.path.join(path, "train_performance.csv")
    test_file = os.path.join(path, "test_performance.csv")
    val_df = pd.read_csv(val_file)
    keys = list(val_df.keys())
    val = t.from_numpy(val_df.values).T
    # test = t.from_numpy(pd.read_csv(test_file).values).squeeze()
    train = t.from_numpy(pd.read_csv(train_file).values).T
    xs = t.arange(val.shape[1])
    train = train[:, : val.shape[1]]
    for i in range(val.shape[0]):
        plt.plot(xs, train[i], "--", label=f"train_{keys[i]}")
        plt.plot(xs, val[i], "--", label=f"val_{keys[i]}")
    # plt.plot([val.shape[1]], [test], "o", label="test")
    plt.legend()
    plt.title("Training")
    plt.savefig(os.path.join(path, "plot.png"))
