import os
import torch as t
import ipdb
import matplotlib.pyplot as plt
from tqdm import tqdm
import h5py
from torch.utils.data import DataLoader, Dataset
from pytorch_lightning import LightningDataModule
from .utils.data_manager import DataManger


class CustomDataModule(LightningDataModule):
    def __init__(self, params):
        super().__init__()
        self.data_location = params.data_location
        self.train_batch_size = params.train_batch_size
        self.test_batch_size = params.test_batch_size
        self.in_seq_len = params.in_seq_len
        self.out_seq_len = params.out_seq_len
        self.crop = params.crop

    def train_dataloader(self):
        # creates a DeepCoastalDataset object
        dataset = CustomDataset(
            self.data_location,
            train=True,
            in_seq_len=self.in_seq_len,
            out_seq_len=self.out_seq_len,
            crop=self.crop,
        )
        return DataLoader(
            dataset, batch_size=self.train_batch_size, drop_last=True, num_workers=3,
        )

    def val_dataloader(self):
        # creates a DeepCoastalDataset object
        dataset = CustomDataset(
            self.data_location,
            train=False,
            in_seq_len=self.in_seq_len,
            out_seq_len=self.out_seq_len,
            crop=self.crop,
        )
        return DataLoader(
            dataset, batch_size=self.train_batch_size, drop_last=True, num_workers=3,
        )

    def test_dataloader(self):
        # creates a DeepCoastalDataset object
        dataset = CustomDataset(
            self.data_location,
            train=False,
            in_seq_len=self.in_seq_len,
            out_seq_len=self.out_seq_len,
            crop=self.crop,
        )
        return DataLoader(
            dataset, batch_size=self.train_batch_size, drop_last=True, num_workers=3,
        )


class CustomDataset(Dataset):
    def __init__(
        self,
        data_location: str = "../datasets/4ch_coastal_normalization.h5",
        in_seq_len: int = 4,
        out_seq_len: int = 4,
        train: bool = True,
        crop: int = 64,
    ):
        self.data_location = data_location
        self.train = train
        self.crop = crop
        with h5py.File(data_location, "r") as f:
            data_manager = DataManger(ranges=f["ranges"])
            raw_data = t.from_numpy(f["train" if "train" else "test"][:]).float()
            data = data_manager.normalize(raw_data)
        # augments the data by creating a list of overlapping segments
        self.in_seq_len = in_seq_len
        self.out_seq_len = out_seq_len
        tot_lenght = self.in_seq_len + self.out_seq_len
        data = data[: (len(data) // tot_lenght) * tot_lenght]
        segments = t.stack(
            tuple(
                data[i : i + tot_lenght, :, :crop, :crop]
                for i in range(len(data) - tot_lenght)
            )
        )
        self.data = segments

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        x = self.data[idx, : self.in_seq_len]
        y = self.data[idx, self.out_seq_len :]
        return x, y


def test():
    data_module = DeepCoastalDataModule()
    train_dataloader = data_module.train_dataloader()
    for i, (x, y) in enumerate(train_dataloader):
        print(i, x.shape, y.shape)
    """
    train_dl, test_dl = get_loaders(
        "/mnt/tmp/multi_channel_train_test",
        32,
        64,
        t.device("cuda" if t.cuda.is_available() else "cpu"),
        in_seq_len=8,
        out_seq_len=4,
    )
    for i, (x, y) in enumerate(tqdm(train_dl)):
        # plt.imshow(x[0, 0, 0].cpu())
        # plt.show()
        # print(x.shape)
        # return
        # print(f"iteration: {i}")
        pass
    """
    # reads file in h5 format


if __name__ == "__main__":
    test()


"""
class DataLoader:
    def __init__(
        self,
        file: str,
        batch_size: int,
        device: t.device,
        train: bool,
        *,
        crop=64,
        shuffle: bool = True,
        in_seq_len: int = 4,
        out_seq_len: int = 4,
    ):
        self.train = train
        self.in_seq_len = in_seq_len
        self.out_seq_len = out_seq_len
        self.tot_seq_len = in_seq_len + out_seq_len
        self.crop = crop
        self.device = device
        self.batch_size = batch_size
        self.file_index = 0
        self.files = (file,)
        self.shuffle = shuffle
        if self.shuffle:
            rand_indices = t.randperm(len(self.files))
            tmp = tuple(self.files[i] for i in rand_indices)
            self.files = tmp
        self.remainder = self.__read_next_file()
        self.file_length = self.remainder.shape[0] * self.remainder.shape[1]

    def __read_next_file(self) -> t.Tensor:
        if self.file_index == len(self.files):
            raise StopIteration
        # reads the next file in h5 format
        with h5py.File(self.files[self.file_index], "r") as f:
            data = t.from_numpy(f["train" if self.train else "test"][:])
        # data = t.load(self.files[self.file_index])
        self.file_index += 1
        result = self.__segmentify(data)
        return result

    def __segmentify(self, data: t.Tensor) -> t.Tensor:
        data = data[: (len(data) // self.tot_seq_len) * self.tot_seq_len]
        if self.crop is not None:
            data = data[:, :, : self.crop, : self.crop]
        return data

    def __next__(self) -> tuple[t.Tensor, t.Tensor]:
        if self.remainder.shape[0] == 0:
            data = self.__read_next_file()
        else:
            data = self.remainder
        self.remainder = data[self.batch_size :]
        segments = tuple(
            data[i : i + self.tot_seq_len]
            for i in range(self.batch_size)
            if len(data[i : i + self.tot_seq_len]) == self.tot_seq_len
        )
        if len(segments) == 0:
            raise StopIteration
        result = t.stack(segments, dim=0)
        if len(result) == 0:
            raise StopIteration
        xs = t.stack(tuple(s[: self.in_seq_len] for s in result))
        ys = t.stack(tuple(s[self.in_seq_len :] for s in result))
        rand_indices = (
            t.randperm(result.shape[0])
            if self.shuffle
            else t.arange(result.shape[0])
        )
        results = (
            xs[rand_indices].float().to(self.device),
            ys[rand_indices].float().to(self.device),
        )
        return results

    def __iter__(self):
        return self


def get_loaders(
    data_location: str,
    train_batch_size: int,
    test_batch_size: int,
    device: t.device,
    *,
    crop: int = 64,
    in_seq_len: int = 12,
    out_seq_len: int = 6,
) -> tuple[DataLoader, DataLoader]:
    return (
        DataLoader(
            data_location,
            train_batch_size,
            device,
            train=True,
            in_seq_len=in_seq_len,
            out_seq_len=out_seq_len,
            crop=crop,
        ),
        DataLoader(
            data_location,
            test_batch_size,
            device,
            train=False,
            in_seq_len=in_seq_len,
            out_seq_len=out_seq_len,
            crop=crop,
        ),
    )
"""
