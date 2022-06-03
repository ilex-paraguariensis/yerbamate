import torch as t
import torch.nn as nn
import torch.nn.functional as F
from pytorch_lightning import LightningModule
from .base_model import BaseModel
import ipdb
import h5py
from .utils.data_manager import DataManger
from .utils.visualize_predictions import visualize_predictions
from argparse import Namespace


class GANLightning(BaseModel):
    def __init__(
        self, params: Namespace,
    ):
        super().__init__(params)

        self.frame_discriminator = nn.Sequential()
        self.temporal_discriminator = nn.Sequential()
        self.fake_y_detached = t.tensor(0.0)

    def adversarial_loss(self, y_hat: t.Tensor, y: t.Tensor):
        return F.binary_cross_entropy(y_hat, y)

    def training_step(
        self, batch: tuple[t.Tensor, t.Tensor], batch_idx: int, optimizer_idx: int
    ):
        x, y = batch
        batch_size, x_seq_len, channels, height, width = x.shape
        batch_size, y_seq_len, channels, height, width = y.shape
        # train generator
        if optimizer_idx == 0:
            fake_y = self(x)
            # i save it as property to avoid recomputing it for the discriminators
            self.fake_y_detached = fake_y.detach()  # used later by discriminators
            fake_data_frames = fake_y.reshape(
                batch_size * y_seq_len, channels, height, width
            )
            pred_frame_label = self.frame_discriminator(fake_data_frames)
            pred_temp_label = self.temporal_discriminator(t.cat((x, fake_y), dim=1))
            real_frame_label = t.ones(batch_size * y_seq_len).to(self.device)
            real_temp_label = t.ones(batch_size).to(self.device)
            generator_loss = self.adversarial_loss(
                pred_temp_label, real_temp_label
            ) + self.adversarial_loss(pred_frame_label, real_frame_label)
            tqdm_dict = {"g_loss": generator_loss}
            # not used for backpropagation
            train_mse = F.mse_loss(fake_y.detach(), y)
            return {
                "loss": generator_loss,
                "progress_bar": tqdm_dict,
                "log": tqdm_dict,
                "train_mse": train_mse,
            }

        # train frame discriminator
        if optimizer_idx == 1:
            # Create labels for the real data. (label=1)
            # x_frames = x.view(batch_size * x_seq_len, channels, height, width)
            y_frames = y.reshape(batch_size * y_seq_len, channels, height, width)
            fake_frames = self.fake_y_detached.reshape(
                batch_size * y_seq_len, channels, height, width
            )
            y_batch_size = batch_size * y_seq_len
            real_label = t.ones(y_batch_size, 1, device=self.device)
            fake_label = t.zeros(y_batch_size, 1, device=self.device)
            labels = t.cat((real_label, fake_label)).squeeze()
            frames = t.cat((y_frames, fake_frames))
            frame_disc_loss = self.adversarial_loss(
                self.frame_discriminator(frames).squeeze(), labels
            )
            tqdm_dict = {"fd_loss": frame_disc_loss}
            return {
                "loss": frame_disc_loss,
                "progress_bar": tqdm_dict,
                "log": tqdm_dict,
            }

        # train temporal discriminator
        if optimizer_idx == 2:
            real_label = t.ones(batch_size, 1, device=self.device)
            fake_label = t.zeros(batch_size, 1, device=self.device)
            labels = t.cat((real_label, fake_label)).squeeze()
            fake_sequence = t.cat((x, self.fake_y_detached), dim=1)
            real_sequence = t.cat((x, y), dim=1)
            sequences = t.cat((real_sequence, fake_sequence))
            pred_labels = self.temporal_discriminator(sequences)
            temp_disc_loss = self.adversarial_loss(pred_labels, labels)
            tqdm_dict = {"td_loss": temp_disc_loss}
            return {
                "loss": temp_disc_loss,
                "progress_bar": tqdm_dict,
                "log": tqdm_dict,
            }

    def training_epoch_end(self, outputs):
        avg_loss = t.stack([x[0]["train_mse"] for x in outputs]).mean()
        self.log("train_mse", avg_loss, prog_bar=True)

    def configure_optimizers(self):
        lr = self.params.lr
        b1 = self.params.b1
        b2 = self.params.b2

        generator_optimizer = t.optim.Adam(
            self.generator.parameters(), lr=lr, betas=(b1, b2)
        )
        frame_discriminator_optimizer = t.optim.Adam(
            self.frame_discriminator.parameters(), lr=lr, betas=(b1, b2)
        )
        temporal_discriminator_optimizer = t.optim.Adam(
            self.temporal_discriminator.parameters(), lr=lr, betas=(b1, b2)
        )
        return (
            [
                generator_optimizer,
                frame_discriminator_optimizer,
                temporal_discriminator_optimizer,
            ],
            [],
        )
