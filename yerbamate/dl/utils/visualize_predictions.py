import numpy as np
import torch as t
import ipdb
import enum
import matplotlib.pyplot as plt
import os


# define a Bunch class
class Bunch(dict):
    def __init__(self, **kw):
        dict.__init__(self, kw)
        self.__dict__ = self


def visualize_predictions(x, y, preds, *, epoch=1, path="", show_plot=False):
    ch_idx = 1
    x = x[:, :, ch_idx]
    y = y[:, :, ch_idx]
    preds = preds[:, :, ch_idx]
    if path != "" and not os.path.exists(path):
        os.mkdir(path)
    to_plot = [x[0], y[0].squeeze(1), preds[0]]
    _, ax = plt.subplots(nrows=len(to_plot), ncols=to_plot[0].shape[0])
    plt.suptitle(f"Epoch {epoch}")
    for i, row in enumerate(ax):
        for j, col in enumerate(row):
            col.imshow(to_plot[i].cpu().detach().numpy()[j])

    row_labels = ["input", "GT", "pred"]
    for ax_, row in zip(ax[:, 0], row_labels):
        ax_.set_ylabel(row)

    col_labels = [f"F{i}" for i in range(to_plot[0].shape[0])]
    for ax_, col in zip(ax[0, :], col_labels):
        ax_.set_title(col)

    save_path = os.path.join(path, f"pred.png")
    if not show_plot:
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()
