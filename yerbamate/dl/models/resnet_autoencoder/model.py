from types import SimpleNamespace
import torch
import torch as t
from torch import nn, optim
import torch.nn.functional as F


class ResizeConv2d(nn.Module):
    def __init__(
        self, in_channels, out_channels, kernel_size, scale_factor, mode="nearest"
    ):
        super().__init__()
        self.scale_factor = scale_factor
        self.mode = mode
        self.conv = nn.Conv2d(
            in_channels, out_channels, kernel_size, stride=1, padding=1
        )

    def forward(self, x):
        x = F.interpolate(x, scale_factor=self.scale_factor, mode=self.mode)
        x = self.conv(x)
        return x


class BasicBlockEnc(nn.Module):
    def __init__(self, in_planes, stride=1):
        super().__init__()

        planes = in_planes * stride

        self.conv1 = nn.Conv2d(
            in_planes, planes, kernel_size=3, stride=stride, padding=1, bias=False
        )
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(
            planes, planes, kernel_size=3, stride=1, padding=1, bias=False
        )
        self.bn2 = nn.BatchNorm2d(planes)

        if stride == 1:
            self.shortcut = nn.Sequential()
        else:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_planes, planes, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes),
            )

    def forward(self, x):
        out = torch.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = torch.relu(out)
        return out


class BasicBlockDec(nn.Module):
    def __init__(self, in_planes, stride=1):
        super().__init__()

        planes = int(in_planes / stride)

        self.conv2 = nn.Conv2d(
            in_planes, in_planes, kernel_size=3, stride=1, padding=1, bias=False
        )
        self.bn2 = nn.BatchNorm2d(in_planes)
        # self.bn1 could have been placed here, but that messes up the order of the layers when printing the class

        if stride == 1:
            self.conv1 = nn.Conv2d(
                in_planes, planes, kernel_size=3, stride=1, padding=1, bias=False
            )
            self.bn1 = nn.BatchNorm2d(planes)
            self.shortcut = nn.Sequential()
        else:
            self.conv1 = ResizeConv2d(
                in_planes, planes, kernel_size=3, scale_factor=stride
            )
            self.bn1 = nn.BatchNorm2d(planes)
            self.shortcut = nn.Sequential(
                ResizeConv2d(in_planes, planes, kernel_size=3, scale_factor=stride),
                nn.BatchNorm2d(planes),
            )

    def forward(self, x):
        out = torch.relu(self.bn2(self.conv2(x)))
        out = self.bn1(self.conv1(out))
        out += self.shortcut(x)
        out = torch.relu(out)
        return out


class ResNet18Enc(nn.Module):
    def __init__(self, num_Blocks=[2, 2, 2, 2], z_dim=10, nc=3):
        super().__init__()
        self.in_planes = 64
        self.z_dim = z_dim
        self.conv1 = nn.Conv2d(nc, 64, kernel_size=3, stride=2, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.layer1 = self._make_layer(BasicBlockEnc, 64, num_Blocks[0], stride=1)
        self.layer2 = self._make_layer(BasicBlockEnc, 128, num_Blocks[1], stride=2)
        self.layer3 = self._make_layer(BasicBlockEnc, 256, num_Blocks[2], stride=2)
        self.layer4 = self._make_layer(BasicBlockEnc, 512, num_Blocks[3], stride=2)
        self.linear = nn.Linear(512, 2 * z_dim)

    def _make_layer(self, BasicBlockEnc, planes, num_Blocks, stride):
        strides = [stride] + [1] * (num_Blocks - 1)
        layers = []
        for stride in strides:
            layers += [BasicBlockEnc(self.in_planes, stride)]
            self.in_planes = planes
        return nn.Sequential(*layers)

    def forward(self, x):
        x = torch.relu(self.bn1(self.conv1(x)))
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = F.adaptive_avg_pool2d(x, 1)
        x = x.view(x.size(0), -1)
        x = self.linear(x)
        mu = x[:, : self.z_dim]
        logvar = x[:, self.z_dim :]
        return mu, logvar


class ResNet18Dec(nn.Module):
    def __init__(self, num_Blocks=[2, 2, 2, 2], z_dim=10, nc=6):
        super().__init__()
        self.in_planes = 512
        self.nc = nc

        self.linear = nn.Linear(z_dim, 512)

        self.layer4 = self._make_layer(BasicBlockDec, 256, num_Blocks[3], stride=2)
        self.layer3 = self._make_layer(BasicBlockDec, 128, num_Blocks[2], stride=2)
        self.layer2 = self._make_layer(BasicBlockDec, 64, num_Blocks[1], stride=2)
        self.layer1 = self._make_layer(BasicBlockDec, 64, num_Blocks[0], stride=1)
        self.conv1 = ResizeConv2d(64, nc, kernel_size=3, scale_factor=2)

    def _make_layer(self, BasicBlockDec, planes, num_Blocks, stride):
        strides = [stride] + [1] * (num_Blocks - 1)
        layers = []
        for stride in reversed(strides):
            layers += [BasicBlockDec(self.in_planes, stride)]
        self.in_planes = planes
        return nn.Sequential(*layers)

    def forward(self, z):
        x = self.linear(z)
        x = x.view(z.size(0), 512, 1, 1)
        x = F.interpolate(x, scale_factor=4)
        x = self.layer4(x)
        x = self.layer3(x)
        x = self.layer2(x)
        x = self.layer1(x)
        x = torch.sigmoid(self.conv1(x))
        x = x.view(x.size(0), self.nc, 64, 64)
        return x


class VAE(nn.Module):
    def __init__(self, params, z_dim=40):
        super().__init__()
        self.encoder = ResNet18Enc(z_dim=z_dim, nc=6)
        self.decoder = ResNet18Dec(z_dim=z_dim, nc=6)

    def forward(self, x, t=None):
        mean, logvar = self.encoder(x)
        z = self.reparameterize(mean, logvar)
        x = self.decoder(z)
        return x

    @staticmethod
    def reparameterize(mean, logvar):
        std = torch.exp(logvar / 2)  # in log-space, squareroot is divide by two
        epsilon = torch.randn_like(std)
        return epsilon * std + mean


class ResNetBlock(nn.Module):
    def __init__(self, c_in, act_fn, subsample=False, c_out=-1):
        """
        Inputs:
            c_in - Number of input features
            act_fn - Activation class constructor (e.g. nn.ReLU)
            subsample - If True, we want to apply a stride inside the block and reduce the output shape by 2 in height and width
            c_out - Number of output features. Note that this is only relevant if subsample is True, as otherwise, c_out = c_in
        """
        super().__init__()
        if not subsample:
            c_out = c_in

        # Network representing F
        self.net = nn.Sequential(
            nn.Conv2d(
                c_in,
                c_out,
                kernel_size=3,
                padding=1,
                stride=1 if not subsample else 2,
                bias=False,
            ),  # No bias needed as the Batch Norm handles it
            nn.BatchNorm2d(c_out),
            act_fn(),
            nn.Conv2d(c_out, c_out, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(c_out),
        )

        # 1x1 convolution with stride 2 means we take the upper left value, and transform it to new output size
        self.downsample = (
            nn.Conv2d(c_in, c_out, kernel_size=1, stride=2) if subsample else None
        )
        self.act_fn = act_fn()

    def forward(self, x):
        z = self.net(x)
        if self.downsample is not None:
            x = self.downsample(x)
        out = z + x
        out = self.act_fn(out)
        return out


class PreActResNetBlock(nn.Module):
    def __init__(self, c_in, act_fn, subsample=False, c_out=-1):
        """
        Inputs:
            c_in - Number of input features
            act_fn - Activation class constructor (e.g. nn.ReLU)
            subsample - If True, we want to apply a stride inside the block and reduce the output shape by 2 in height and width
            c_out - Number of output features. Note that this is only relevant if subsample is True, as otherwise, c_out = c_in
        """
        super().__init__()
        if not subsample:
            c_out = c_in

        # Network representing F
        self.net = nn.Sequential(
            nn.BatchNorm2d(c_in),
            act_fn(),
            nn.Conv2d(
                c_in,
                c_out,
                kernel_size=3,
                padding=1,
                stride=1 if not subsample else 2,
                bias=False,
            ),
            nn.BatchNorm2d(c_out),
            act_fn(),
            nn.Conv2d(c_out, c_out, kernel_size=3, padding=1, bias=False),
        )

        # 1x1 convolution needs to apply non-linearity as well as not done on skip connection
        self.downsample = (
            nn.Sequential(
                nn.BatchNorm2d(c_in),
                act_fn(),
                nn.Conv2d(c_in, c_out, kernel_size=1, stride=2, bias=False),
            )
            if subsample
            else None
        )

    def forward(self, x):
        z = self.net(x)
        if self.downsample is not None:
            x = self.downsample(x)
        out = z + x
        return out


resnet_blocks_by_name = {
    "ResNetBlock": ResNetBlock,
    "PreActResNetBlock": PreActResNetBlock,
}
act_fn_by_name = {
    "tanh": nn.Tanh,
    "relu": nn.ReLU,
    "leakyrelu": nn.LeakyReLU,
    "gelu": nn.GELU,
}


class FrameDiscriminator(nn.Module):
    def __init__(
        self,
        params,
        num_blocks=[3, 3, 3],
        c_hidden=[16, 32, 64],
        act_fn_name="relu",
        block_name="ResNetBlock",
        **kwargs
    ):
        """
        Inputs:
            num_classes - Number of classification outputs (10 for CIFAR10)
            num_blocks - List with the number of ResNet blocks to use. The first block of each group uses downsampling, except the first.
            c_hidden - List with the hidden dimensionalities in the different blocks. Usually multiplied by 2 the deeper we go.
            act_fn_name - Name of the activation function to use, looked up in "act_fn_by_name"
            block_name - Name of the ResNet block, looked up in "resnet_blocks_by_name"
        """
        super().__init__()
        self.params = params
        assert block_name in resnet_blocks_by_name
        self.hparams = SimpleNamespace(
            c_hidden=c_hidden,
            num_blocks=num_blocks,
            act_fn_name=act_fn_name,
            act_fn=act_fn_by_name[act_fn_name],
            block_class=resnet_blocks_by_name[block_name],
        )
        self._create_network()
        self._init_params()

    def _create_network(self):
        c_hidden = self.hparams.c_hidden

        # A first convolution on the original image to scale up the channel size
        if (
            self.hparams.block_class == PreActResNetBlock
        ):  # => Don't apply non-linearity on output
            self.input_net = nn.Sequential(
                nn.Conv2d(
                    self.params["nc"], c_hidden[0], kernel_size=3, padding=1, bias=False
                )
            )
        else:
            self.input_net = nn.Sequential(
                nn.Conv2d(
                    self.params["nc"], c_hidden[0], kernel_size=3, padding=1, bias=False
                ),
                nn.BatchNorm2d(c_hidden[0]),
                self.hparams.act_fn(),
            )

        # Creating the ResNet blocks
        blocks = []
        for block_idx, block_count in enumerate(self.hparams.num_blocks):
            for bc in range(block_count):
                subsample = (
                    bc == 0 and block_idx > 0
                )  # Subsample the first block of each group, except the very first one.
                blocks.append(
                    self.hparams.block_class(
                        c_in=c_hidden[block_idx if not subsample else (block_idx - 1)],
                        act_fn=self.hparams.act_fn,
                        subsample=subsample,
                        c_out=c_hidden[block_idx],
                    )
                )
        self.blocks = nn.Sequential(*blocks)

        # Mapping to classification output
        self.output_net = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(c_hidden[-1], 1),
            nn.Sigmoid(),
        )

    def _init_params(self):
        # Based on our discussion in Tutorial 4, we should initialize the convolutions according to the activation function
        # Fan-out focuses on the gradient distribution, and is commonly used in ResNets
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(
                    m.weight, mode="fan_out", nonlinearity=self.hparams.act_fn_name
                )
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):

        # noise_matrix_w_h = 12
        # noise = t.randn( self.params['nc'] , noise_matrix_w_h, noise_matrix_w_h)

        # x_concat = t.zeros((x.shape[0], x.shape[1], x.shape[2]+ noise_matrix_w_h, x.shape[3]+ noise_matrix_w_h))
        # x_concat[:,:,:x.shape[2], :x.shape[3]] = x
        # x_concat[:,:,x.shape[2]:, x.shape[3]:] = noise

        x = self.input_net(x)
        x = self.blocks(x)
        x = self.output_net(x)
        return x.squeeze()


class TemporalDiscriminator(nn.Module):
    def __init__(
        self,
        params,
        num_blocks=[3, 3, 3],
        c_hidden=[16, 32, 64],
        act_fn_name="relu",
        block_name="ResNetBlock",
        **kwargs
    ):
        """
        Inputs:
            num_classes - Number of classification outputs (10 for CIFAR10)
            num_blocks - List with the number of ResNet blocks to use. The first block of each group uses downsampling, except the first.
            c_hidden - List with the hidden dimensionalities in the different blocks. Usually multiplied by 2 the deeper we go.
            act_fn_name - Name of the activation function to use, looked up in "act_fn_by_name"
            block_name - Name of the ResNet block, looked up in "resnet_blocks_by_name"
        """
        super().__init__()
        self.params = params

        assert block_name in resnet_blocks_by_name
        self.hparams = SimpleNamespace(
            c_hidden=c_hidden,
            num_blocks=num_blocks,
            act_fn_name=act_fn_name,
            act_fn=act_fn_by_name[act_fn_name],
            block_class=resnet_blocks_by_name[block_name],
        )
        self._create_network()
        self._init_params()

    def _create_network(self):
        c_hidden = self.hparams.c_hidden

        # A first convolution on the original image to scale up the channel size
        if (
            self.hparams.block_class == PreActResNetBlock
        ):  # => Don't apply non-linearity on output
            self.input_net = nn.Sequential(
                nn.Conv2d(
                    self.params["nc"] * 2,
                    c_hidden[0],
                    kernel_size=3,
                    padding=1,
                    bias=False,
                )
            )
        else:
            self.input_net = nn.Sequential(
                nn.Conv2d(
                    self.params["nc"] * 2,
                    c_hidden[0],
                    kernel_size=3,
                    padding=1,
                    bias=False,
                ),
                nn.BatchNorm2d(c_hidden[0]),
                self.hparams.act_fn(),
            )

        # Creating the ResNet blocks
        blocks = []
        for block_idx, block_count in enumerate(self.hparams.num_blocks):
            for bc in range(block_count):
                subsample = (
                    bc == 0 and block_idx > 0
                )  # Subsample the first block of each group, except the very first one.
                blocks.append(
                    self.hparams.block_class(
                        c_in=c_hidden[block_idx if not subsample else (block_idx - 1)],
                        act_fn=self.hparams.act_fn,
                        subsample=subsample,
                        c_out=c_hidden[block_idx],
                    )
                )
        self.blocks = nn.Sequential(*blocks)

        # Mapping to classification output
        self.output_net = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(c_hidden[-1], 1),
            nn.Sigmoid(),
        )

    def _init_params(self):
        # Based on our discussion in Tutorial 4, we should initialize the convolutions according to the activation function
        # Fan-out focuses on the gradient distribution, and is commonly used in ResNets
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(
                    m.weight, mode="fan_out", nonlinearity=self.hparams.act_fn_name
                )
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):

        # noise_matrix_w_h = 12
        # noise = t.randn( self.params['nc'] * 2, noise_matrix_w_h, noise_matrix_w_h)

        # x_concat = t.zeros((x.shape[0], x.shape[1], x.shape[2]+ noise_matrix_w_h, x.shape[3]+ noise_matrix_w_h))
        # x_concat[:,:,:x.shape[2], :x.shape[3]] = x
        # x_concat[:,:,x.shape[2]:, x.shape[3]:] = noise

        x = self.input_net(x)
        x = self.blocks(x)
        x = self.output_net(x)
        return x.squeeze()
