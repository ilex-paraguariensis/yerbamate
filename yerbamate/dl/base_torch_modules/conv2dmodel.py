from turtle import forward
from typing import List
from numpy import pad
import torch as t
import torch.nn as nn
import torch.nn.functional as F
import ipdb

# from .axial_attention import AxialAttention, AxialPositionalEmbedding, AxialImageTransformer
import ipdb


def weights_init(w):
    """
    Initializes the weights of the layer, w.
    """
    classname = w.__class__.__name__
    # if isinstance(w, nn.Conv3d):
    #     nn.init.kaiming_normal_(w.weight,mode='fan_out',  nonlinearity='relu')
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
        batchnorm=True
    ):
        super().__init__()
        layers: list[nn.Module] = [
            nn.Conv2d(
                chin,
                chout,
                kernel_size=kernel_size,
                stride=stride,
                padding=padding,
                bias=bias,
            )
        ]
        if batchnorm:
            layers.append(nn.BatchNorm2d(chout))
        if dropout > 0:
            layers.append(nn.Dropout2d(dropout))

        self.act = act
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


# class ConvGenerator(nn.Module):
#     def __init__(self, params):
#         super().__init__()
#         self.params = params
#         # Input is the latent vector Z.

#         self.layers = nn.Sequential(
#             GaussianNoise(0.001),
#             # AxialPositionalEmbedding( params['nc'], (params['imsize'], params['imsize'])),
#             ConvBlock(
#                 params["nc"], params["nc"] * 24, kernel_size=4, padding="same"
#             ),
#             ConvBlock(params["nc"] * 24, params["nc"] * 12, 4, padding="same"),
#             ConvBlock(params["nc"] * 12, params["nc"] * 8, 4, padding="same"),
#             ConvBlock(params["nc"] * 8, params["nc"] * 2, 4, padding="same"),
#             ConvBlock(params["nc"] * 2, params["nc"] * 1, 4, padding="same"),
#             ConvBlock(
#                 params["nc"],
#                 params["nc"],
#                 4,
#                 padding="same",
#                 act=t.sigmoid,
#                 batchnorm=False,
#             ),
#         )

#     def forward(self, x):
#         return self.layers(x)


class ProbablisticConvGenerator(nn.Module):
    def __init__(self, params):
        super().__init__()
        self.params = params
        # Input is the latent vector Z.

        self.noise_layer = GaussianNoise(0.001)
        mlp = 1  # multiplier of the number of channels
        # random noise matrix with batch size, channels, height, width

        self.layers = nn.Sequential(
            # GaussianNoise(0.001),
            ConvBlock(
                params.n_channels,
                params.n_channels * 18 * mlp,
                kernel_size=4,
                padding="same",
            ),
            ConvBlock(
                params.n_channels * 18 * mlp,
                params.n_channels * 12 * mlp,
                4,
                padding="same",
            ),
            ConvBlock(
                params.n_channels * 12 * mlp,
                params.n_channels * 8 * mlp,
                4,
                padding="same",
            ),
            ConvBlock(
                params.n_channels * 8 * mlp,
                params.n_channels * 4 * mlp,
                4,
                padding="same",
            ),
            ConvBlock(params.n_channels * mlp * 2, params.n_channels * 1, 1),
            # ConvBlock(params["nc"] * 8, params["nc"] * 12, 1 ),
            # ConvBlock(params["nc"] * 12, params["nc"] * 24, 1),
            # ConvBlock(params["nc"] * 24, params["nc"] * 12, 1),
            # ConvBlock(params["nc"] * 8, params["nc"] * 1, 1),
            # ConvBlock(
            #     params["nc"],
            #     params["nc"],
            #     1,
            #     padding="same",
            #     act=t.sigmoid,
            #     batchnorm=False,
            # ),
        )

    def forward(self, x, noiseVariance=0.001):

        # if noiseVariance == None:
        #     return self.layers(x)

        # else:
        #     self.noise_layer.variance = 0.001 # t.FloatTensor(1).uniform_(noiseVariance, noiseVariance*2).to(x.device)
        # print(self.noise_layer.variance)

        # noise is a random
        noise_matrix_w_h = 12
        noise = t.randn(self.params.n_channels, 1, noise_matrix_w_h)

        x_concat = t.zeros(
            (x.shape[0], x.shape[1], x.shape[2] + 1, x.shape[3] + noise_matrix_w_h)
        )
        x_concat[:, :, : x.shape[2], : x.shape[3]] = x
        x_concat[:, :, x.shape[2] :, x.shape[3] :] = noise

        return self.layers(x)


class ConvGenerator(nn.Module):
    def __init__(self, params):
        super().__init__()
        self.params = params
        # Input is the latent vector Z.

        self.noise_layer = GaussianNoise(0.001)
        mlp = 1  # multiplier of the number of channels
        # random noise matrix with batch size, channels, height, width

        self.layers = nn.Sequential(
            GaussianNoise(0.001),
            ConvBlock(
                params.n_channels,
                params.n_channels * 18 * mlp,
                kernel_size=4,
                padding="same",
            ),
            ConvBlock(
                params.n_channels * 18 * mlp,
                params.n_channels * 12 * mlp,
                4,
                padding="same",
            ),
            ConvBlock(
                params.n_channels * 12 * mlp,
                params.n_channels * 8 * mlp,
                4,
                padding="same",
            ),
            ConvBlock(
                params.n_channels * 8 * mlp,
                params.n_channels * 2 * mlp,
                4,
                padding="same",
            ),
            ConvBlock(params.n_channels * mlp * 2, params.n_channels * 1, 1),
            # ConvBlock(params["nc"] * 8, params["nc"] * 12, 1 ),
            # ConvBlock(params["nc"] * 12, params["nc"] * 24, 1),
            # ConvBlock(params["nc"] * 24, params["nc"] * 12, 1),
            # ConvBlock(params["nc"] * 8, params["nc"] * 1, 1),
            ConvBlock(
                params.n_channels,
                params.n_channels,
                1,
                padding="same",
                act=t.sigmoid,
                batchnorm=False,
            ),
        )

    def forward(self, x, noiseVariance=0.001):

        return self.layers(x)


class TemporalDiscriminator(nn.Module):
    def __init__(self, params):
        super().__init__()
        nc = params.n_channels
        ndf = params.ndf

        def act(x):
            return F.leaky_relu(x, 0.2, True)

        self.layers = nn.Sequential(
            *[
                # ConvBlock(2 * nc, ndf , 4, act=act, batchnorm=False),
                ConvBlock(
                    params.in_seq_len + params.out_seq_len,
                    ndf,
                    kernel_size=4,
                    stride=2,
                    bias=True,
                    batchnorm=False,
                    padding=1,
                    act=act,
                ),
                ConvBlock(
                    ndf,
                    2 * ndf,
                    kernel_size=4,
                    stride=2,
                    padding=1,
                    bias=True,
                    act=act,
                ),
                ConvBlock(
                    2 * ndf,
                    4 * ndf,
                    kernel_size=4,
                    stride=2,
                    padding=1,
                    bias=True,
                    act=act,
                ),
                ConvBlock(
                    4 * ndf,
                    8 * ndf,
                    kernel_size=4,
                    stride=2,
                    padding=1,
                    bias=True,
                    act=act,
                ),
                ConvBlock(
                    8 * ndf,
                    1,
                    kernel_size=4,
                    stride=4,
                    padding=0,
                    bias=True,
                    batchnorm=False,
                    act=t.sigmoid,
                ),
                # nn.Flatten( 64 * 64 * 6 ),
                # nn.Linear(128, 1),
                # nn.Sigmoid()
            ]
        )

    def forward(self, x):
        # ipnb.set_trace()

        x = self.layers(x)
        return x.squeeze()


class FrameDiscriminator(nn.Module):
    def __init__(self, params):
        super().__init__()

        # Input Dimension: (nc) x 64 x 64
        self.conv1 = nn.Conv2d(params.n_channels, params.ndf, 4, 2, 1, bias=False)

        # Input Dimension: (ndf) x 32 x 32
        self.conv2 = nn.Conv2d(params.ndf, params.ndf * 2, 4, 2, 1, bias=False)
        self.bn2 = nn.BatchNorm2d(params.ndf * 2)

        # Input Dimension: (ndf*2) x 16 x 16
        self.conv3 = nn.Conv2d(params.ndf * 2, params.ndf * 4, 4, 2, 1, bias=False)
        self.bn3 = nn.BatchNorm2d(params.ndf * 4)

        # Input Dimension: (ndf*4) x 8 x 8
        self.conv4 = nn.Conv2d(params.ndf * 4, params.ndf * 8, 4, 2, 1, bias=False)
        self.bn4 = nn.BatchNorm2d(params.ndf * 8)

        # Input Dimension: (ndf*8) x 4 x 4
        self.conv5 = nn.Conv2d(params.ndf * 8, 1, 4, 1, 0, bias=False)

    def forward(self, x):
        x = F.leaky_relu(self.conv1(x), 0.2, True)
        x = F.leaky_relu(self.bn2(self.conv2(x)), 0.2, True)
        x = F.leaky_relu(self.bn3(self.conv3(x)), 0.2, True)
        x = F.leaky_relu(self.bn4(self.conv4(x)), 0.2, True)

        x = t.sigmoid(self.conv5(x))

        return x.squeeze()
