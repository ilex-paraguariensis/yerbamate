from ...base_gan_model import GANLightning
from ...models_components.conv3dmodel import (
    Conv3DGenerator,
    Conv3DTemporalDiscriminator,
)
from ...models_components.conv2dmodel import FrameDiscriminator
from argparse import Namespace


class Model(GANLightning):
    def __init__(self, params: Namespace):
        super().__init__()
        self.generator = Conv3DGenerator(params)
        self.temporal_discriminator = Conv3DTemporalDiscriminator(params)
        self.frame_discriminator = FrameDiscriminator(params)
