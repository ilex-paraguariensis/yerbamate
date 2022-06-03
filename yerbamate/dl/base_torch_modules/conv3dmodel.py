import torch as t
import torch.nn as nn
import torch.nn.functional as F
import ipdb

# from axial_attention import AxialAttention, AxialPositionalEmbedding, AxialImageTransformer
import ipdb

from .dense_layer import (
    AVGPool3DConcatDenseLayer,
    AVGPool3DDenseClassifer,
    SimpleOneLayerClassifer,
)


def weights_init(w):
    """
    Initializes the weights of the layer, w.
    """
    classname = w.__class__.__name__
    if classname.find("conv") != -1:
        nn.init.normal_(w.weight.data, 0.0, 0.02)
    elif classname.find("bn") != -1:
        nn.init.normal_(w.weight.data, 1.0, 0.02)
        nn.init.constant_(w.bias.data, 0)
    elif classname.find("axial") != -1:
        nn.init.normal_(w.weight.data, 1.0, 0.02)
    elif classname.find("resnet") != -1:
        nn.init.normal_(w.weight.data, 1.0, 0.02)


class ConvBlock(nn.Module):
    def __init__(
        self,
        chin: int,
        chout: int,
        kernel_size: int,
        *,
        bias=True,
        stride=1,
        padding=0,
        dropout=0.01,
        act=F.relu,
        batchnorm=True,
        dilation=1
    ):
        super().__init__()
        layers: list[nn.Module] = [
            nn.Conv3d(
                chin,
                chout,
                kernel_size=kernel_size,
                stride=stride,
                padding=padding,
                bias=bias,
                # padding_mode='circular',
                dilation=dilation,
            )
        ]
        if batchnorm:
            layers.append(nn.BatchNorm3d(chout))
        if dropout > 0:
            layers.append(nn.Dropout3d(dropout))

        self.act = act
        if act == t.prelu:
            self.act = nn.PReLU(32)
        # if act==t.sigmoid:
        #     layers.append( nn.Sigmoid())
        # else:
        #     layers.append(nn.ReLU())

        # self.act = act
        self.layers = nn.Sequential(*layers)

    def forward(self, x):
        return self.act(self.layers(x))


class GaussianNoise(nn.Module):
    def __init__(self, variance=0.01):
        super().__init__()
        self.variance = variance

    def forward(self, x):
        noise = t.randn_like(x) * self.variance
        x = ((noise + x).detach() - x).detach() + x
        return x


# uses channels as time sequences
class ConvGenerator(nn.Module):
    def __init__(self, params):
        super().__init__()
        self.params = params
        # Input is the latent vector Z.

        # self.noise_layer = GaussianNoise(0.001);
        mlp = 4  # multiplier of the number of channels
        # random noise matrix with batch size, channels, height, width

        self.layers = nn.Sequential(
            GaussianNoise(params.gaussian_noise_std),
            ConvBlock(
                params.in_seq_len,
                mlp * 18 * mlp,
                kernel_size=4,
                padding="same",
                dropout=False,
            ),
            ConvBlock(
                mlp * 18 * mlp, mlp * 12 * mlp, 4, padding="same", dropout=False,
            ),
            ConvBlock(mlp * 12 * mlp, mlp * 8 * mlp, 4, padding="same", dropout=False),
            ConvBlock(
                mlp * 8 * mlp,
                mlp * 2 * mlp,
                4,
                padding="same",
                dropout=False,
                act=t.prelu,
            ),
            ConvBlock(
                mlp * 2 * mlp,
                params.out_seq_len,
                4,
                padding="same",
                act=t.sigmoid,
                batchnorm=False,
                dropout=False,
            ),
        )

    def forward(self, x):
        # ipdb.set_trace()

        x = x.permute(0, 1, 3, 4, 2)

        x = self.layers(x)
        # x = x.squeeze(1)
        # ipdb.set_trace()
        x = x.permute(0, 1, 4, 2, 3)
        # ipdb.set_trace()

        return x


# uses depth as time sequences
class Conv3DGenerator(nn.Module):
    def __init__(self, params):
        super().__init__()
        self.params = params
        # Input is the latent vector Z.

        # self.noise_layer = GaussianNoise(0.001);
        mlp = 4  # multiplier of the number of channels
        # random noise matrix with batch size, channels, height, width

        self.layers = nn.Sequential(
            GaussianNoise(0.0001),
            Conv3DEncoderBlock(
                params, in_channel=params.n_channels, channels=[32, 64, 128, 256, 512],
            ),
            ConvBlock(
                512,
                params.n_channels,
                params.out_seq_len,
                padding="same",
                act=t.sigmoid,
                batchnorm=False,
                dropout=False,
            ),
        )

    def forward(self, x):
        # ipdb.set_trace()

        x = x.permute(0, 2, 3, 4, 1)

        x = self.layers(x)
        # x = x.squeeze(1)
        # ipdb.set_trace()
        x = x.permute(0, 4, 1, 2, 3)
        # ipdb.set_trace()

        return x


class Conv3DEncoderBlock(nn.Module):
    def __init__(self, params, in_channel=1, channels=[32, 64, 128]) -> None:
        super().__init__()

        # print(channels)
        self.params = params
        c_in = in_channel
        # self.layers = nn.Sequential(
        #     ConvBlock(c_in, channels[0], 4, padding="same", dropout=True),
        # )
        layers = []
        for c_out in channels:
            layers.append(ConvBlock(c_in, c_out, 4, padding="same"))
            c_in = c_out
        self.layers = nn.Sequential(*layers)

    def forward(self, x):
        return self.layers(x)


class Conv3DTemporalDiscriminator(nn.Module):
    def __init__(self, params):
        super().__init__()
        ndf = 4

        self.layers = nn.Sequential(
            # ConvBlock(2 * nc, ndf , 4, act=act, batchnorm=False),
            # Conv3DEncoderBlock(params, in_channel=params['nc'], channels=[ 16, 16, 1]),
            ConvBlock(
                params.n_channels,
                ndf,
                kernel_size=4,
                act=t.rrelu,
                batchnorm=True,
                padding="same",
            ),
            ConvBlock(
                ndf,
                2 * ndf,
                kernel_size=4,
                act=t.rrelu,
                batchnorm=True,
                padding="same",
            ),
            ConvBlock(
                2 * ndf,
                4 * ndf,
                kernel_size=4,
                act=t.rrelu,
                batchnorm=True,
                padding="same",
            ),
            ConvBlock(
                4 * ndf,
                8 * ndf,
                kernel_size=4,
                act=t.rrelu,
                batchnorm=True,
                padding="same",
            ),
            ConvBlock(
                8 * ndf, 1, kernel_size=4, act=t.rrelu, batchnorm=False, padding="same",
            ),
            # nn.Flatten(),
            # nn.Linear( 81920, 1),
            # nn.Sigmoid()
            # AVGPool3DConcatDenseLayer( params, 1 ,params['in_seq_len'] + params['out_seq_len'], params['imsize'], 64),
            SimpleOneLayerClassifer(
                params,
                (
                    1
                    * (params.in_seq_len + params.out_seq_len)
                    * params.imsize
                    * params.imsize
                ),
            ),
        )

    def forward(self, x):
        x = x.permute(0, 2, 3, 4, 1)

        x = self.layers(x)
        # ipdb.set_trace()

        return x


# t.leaky_relu = F.leaky_relu(x, 0.2, True)
class Conv3DFrameDiscriminator(nn.Module):
    def __init__(self, params):
        super().__init__()
        # params['ndf'] = 3

        # Input Dimension: (nc) x 64 x 64
        self.layers = nn.Sequential(
            # Conv3DEncoderBlock(params, in_channel=params['nc'], channels=[ 16, 32, 1]),
            ConvBlock(
                params.n_channels,
                params.ndf,
                4,
                act=t.rrelu,
                batchnorm=True,
                padding="same",
            ),
            ConvBlock(
                params.ndf,
                params.ndf * 2,
                4,
                act=t.rrelu,
                batchnorm=True,
                padding="same",
            ),
            ConvBlock(
                params.ndf * 2,
                params.ndf * 4,
                4,
                act=t.rrelu,
                batchnorm=True,
                padding="same",
            ),
            ConvBlock(
                params.ndf * 4,
                params.ndf * 8,
                4,
                act=t.rrelu,
                batchnorm=True,
                padding="same",
            ),
            ConvBlock(
                params.ndf * 8, 1, 4, act=t.rrelu, batchnorm=False, padding="same",
            ),
            SimpleOneLayerClassifer(
                params, (1 * (params.out_seq_len) * params.imsize * params.imsize),
            ),
        )

    def forward(self, x):
        x = x.permute(0, 2, 3, 4, 1)
        # ipdb.set_trace()

        x = self.layers(x)
        # for layer in self.layers:
        #     x = layer(x)
        # ipdb.set_trace()
        return x
