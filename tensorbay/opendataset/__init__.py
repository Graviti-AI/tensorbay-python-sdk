#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""OpenDataset dataloader collections."""

from .AnimalPose import AnimalPose5, AnimalPose7
from .AnimalsWithAttributes2 import AnimalsWithAttributes2
from .BSTLD import BSTLD
from .CADC import CADC
from .CarConnection import CarConnection
from .CoinImage import CoinImage
from .CompCars import CompCars
from .DeepRoute import DeepRoute
from .DogsVsCats import DogsVsCats
from .DownsampledImagenet import DownsampledImagenet
from .Elpv import Elpv
from .FLIC import FLIC
from .Flower import Flower17, Flower102
from .FSDD import FSDD
from .HardHatWorkers import HardHatWorkers
from .HeadPoseImage import HeadPoseImage
from .ImageEmotion import ImageEmotionAbstract, ImageEmotionArtphoto
from .JHU_CROWD import JHU_CROWD
from .KenyanFood import KenyanFoodOrNonfood, KenyanFoodType
from .KylbergTexture import KylbergTexture
from .LeedsSportsPose import LeedsSportsPose
from .LISATrafficLight import LISATrafficLight
from .NeolixOD import NeolixOD
from .Newsgroups20 import Newsgroups20
from .NightOwls import NightOwls
from .RP2K import RP2K
from .THCHS30 import THCHS30
from .THUCNews import THUCNews
from .TLR import TLR
from .WIDER_FACE import WIDER_FACE

__all__ = [
    "AnimalPose5",
    "AnimalPose7",
    "AnimalsWithAttributes2",
    "BSTLD",
    "CADC",
    "CarConnection",
    "CoinImage",
    "CompCars",
    "DeepRoute",
    "DogsVsCats",
    "DownsampledImagenet",
    "Elpv",
    "FLIC",
    "FSDD",
    "Flower102",
    "Flower17",
    "HardHatWorkers",
    "HeadPoseImage",
    "ImageEmotionAbstract",
    "ImageEmotionArtphoto",
    "JHU_CROWD",
    "KenyanFoodOrNonfood",
    "KenyanFoodType",
    "KylbergTexture",
    "LISATrafficLight",
    "LeedsSportsPose",
    "NeolixOD",
    "Newsgroups20",
    "NightOwls",
    "RP2K",
    "THCHS30",
    "THUCNews",
    "TLR",
    "WIDER_FACE",
]
