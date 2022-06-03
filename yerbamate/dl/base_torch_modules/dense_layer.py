from turtle import forward
import ipdb
import torch as t
import torch.nn as nn


class AVGPool3DDenseClassifer(nn.Module):
    def __init__(self, c_hidden) -> None:
        super().__init__()
        self.output_net = nn.Sequential(
            nn.AdaptiveAvgPool3d((1, 1, 1)),
            nn.Flatten(),
            nn.Linear(c_hidden, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.output_net(x)


class AVGPoolDenseClassifer(nn.Module):
    def __init__(self, c_hidden) -> None:
        super().__init__()
        self.output_net = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(c_hidden, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.output_net(x)


class DenseLayerClassifier(nn.Module):
    def __init__(self, params, c_hidden, nf=256):
        super.__init__(self)

        self.params = params
        self.c_hidden = c_hidden

        self.img_flat_size = params["imsize"] ** 2 * c_hidden

        self.dense_layer = nn.Sequential(
            nn.Linear(params["imsize"] ** 2 * c_hidden + c_hidden, 2 * nf),
            #  nn.ReLU(0.2, 0.3),
            #  nn.ReLU(),
            nn.Linear(2 * nf, nf),
            nn.LeakyReLU(0.2, inplace=True),
            #  nn.RReLU(0.2, 0.3),
            # #  nn.ReLU(),
            nn.Linear(nf, 1),
            nn.LeakyReLU(0.2, inplace=True),
            # nn.PReLU(),
            nn.Sigmoid(),
        )

    def forward(self, x):
        x = self.dense_layer(x)
        return x


class SimpleOneLayerClassifer(nn.Module):
    def __init__(self, params, input_size):
        super().__init__()

        self.layers = nn.Sequential(
            nn.Flatten(),
            nn.Linear(input_size, 1024),
            nn.ReLU(),
            nn.Linear(1024, 1),
            # nn.ReLU(),
            # nn.Linear(512, 1),
            # nn.ReLU(),
            # nn.Linear(256, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.layers(x)


# A DenseLayer For 3D Data Classification
class AVGPool3DConcatDenseLayer(nn.Module):
    def __init__(
        self, params, c_hidden, depth, imsize, hf, num_layers=4, concat_full_image=False
    ):
        super(AVGPool3DConcatDenseLayer, self).__init__()

        self.params = params
        self.c_hidden = c_hidden

        self.img_flat_size = imsize ** 2
        input_size = c_hidden * self.img_flat_size * depth
        # self.dense_layers = []
        self.dense_layer = nn.Sequential(nn.Dropout(0.2), nn.Flatten())
        # self.concat_full_image = concat_full_image

        # if not self.concat_full_image:
        #     self.dense_layer = AVGPool3DDenseClassifer(c_hidden)
        #     return

        for i in range(num_layers):
            backward_i = num_layers - i - 1

            if i != num_layers - 1:
                self.dense_layer.append(nn.Linear(input_size, hf * (2 ** backward_i)))
                self.dense_layer.append(nn.ReLU())
            else:
                self.dense_layer.append(nn.Linear(input_size, 1))
                self.dense_layer.append(nn.Sigmoid())

            input_size = hf * (2 ** backward_i)

        self.avg_pool_layer = nn.Sequential(
            nn.AdaptiveAvgPool3d((1, 1, 1)), nn.Flatten(),
        )

    def forward(self, x):

        # ipdb.set_trace()
        # if not self.concat_full_image:
        #     return self.dense_layer(x)

        original_x = x
        # avg_pool = self.avg_pool_layer(x)

        # ipdb.set_trace()
        # x = t.cat((original_x.flatten(1) , avg_pool), 1)

        x = self.dense_layer(x)
        return x


# A DenseLayer For ResNet Classification
class AVGPoolConcatDenseLayer(nn.Module):
    def __init__(
        self, params, c_hidden, imsize, hf, num_layers=4, concat_full_image=False
    ):
        super(AVGPoolConcatDenseLayer, self).__init__()

        self.params = params
        self.c_hidden = c_hidden

        self.img_flat_size = (imsize ** 2) * c_hidden + c_hidden
        input_size = self.img_flat_size
        # self.dense_layers = []
        self.dense_layer = nn.Sequential(nn.Dropout(0.2),)
        self.concat_full_image = concat_full_image

        if not self.concat_full_image:
            self.dense_layer = AVGPoolDenseClassifer(c_hidden)
            return

        for i in range(num_layers):
            backward_i = num_layers - i - 1

            if i != num_layers - 1:
                self.dense_layer.append(nn.Linear(input_size, hf * (2 ** backward_i)))
                self.dense_layer.append(nn.ReLU())
            else:
                self.dense_layer.append(nn.Linear(input_size, 1))
                self.dense_layer.append(nn.Sigmoid())

            input_size = hf * (2 ** backward_i)

        self.avg_pool_layer = nn.Sequential(nn.AdaptiveAvgPool2d((1, 1)), nn.Flatten(),)

    def forward(self, x):

        if not self.concat_full_image:
            return self.dense_layer(x)

        original_x = x
        avg_pool = self.avg_pool_layer(x)

        # ipdb.set_trace()
        x = t.cat((original_x.flatten(1), avg_pool), 1)

        x = self.dense_layer(x)
        return x
