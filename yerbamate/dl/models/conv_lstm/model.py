from gan.models.conv_lstm.old_model import EncoderDecoderConvLSTM
from ...base_gan_model import GANLightning
from ...models_components.resnet3d import (
    ResNet3DAutoEncoder,
    ResNet3DClassifier,
)
from ...models_components.conv2dmodel import FrameDiscriminator
from argparse import Namespace


class Model(GANLightning):
    def __init__(self, params: Namespace):
        super().__init__(params)
        self.generator = EncoderDecoderConvLSTM(params)
        self.temporal_discriminator = ResNet3DClassifier(params)
        self.frame_discriminator = FrameDiscriminator(params)
