import h5py
import torch as t
import ipdb


class DataManger:
    def __init__(self, *, data_path=None, ranges=None):
        if data_path is not None:
            self.ranges = t.from_numpy(h5py.File(data_path, "r")["ranges"][...])
        elif ranges is not None:
            self.ranges = ranges
        else:
            raise ValueError("data_path or ranges must be specified")

    def normalize(self, data: t.Tensor, device=None):
        max_val = self.ranges[:, 0][None, :, None, None]
        min_val = self.ranges[:, -1][None, :, None, None]
        normalized = 0.1 + 0.9 * (data - min_val) / (max_val - min_val)
        return normalized

    def denormalize(self, data: t.Tensor, device=None):
        device = device or t.device("cpu")
        max_val = self.ranges[:, 0][None, :, None, None].to(device)
        min_val = self.ranges[:, -1][None, :, None, None].to(device)
        return ((data - 0.1) * (max_val - min_val)) / 0.9 - max_val

    def discretize(self, data, device=None):
        device = device or t.device("cpu")
        threshold = self.ranges[:, 1][None, :, None, None].to(device)
        return data > threshold
