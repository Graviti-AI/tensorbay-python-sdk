#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""OpenDataset dataloader collections."""

from .AADB import AADB
from .AnimalPose import AnimalPose5, AnimalPose7
from .AnimalsWithAttributes2 import AnimalsWithAttributes2
from .BDD100K import BDD100K
from .BioIDFace import BioIDFace
from .BSTLD import BSTLD
from .CACD import CACD
from .CADC import CADC
from .CarConnection import CarConnection
from .CCPD import CCPD, CCPDGreen
from .CoinImage import CoinImage
from .CompCars import CompCars
from .COVID_CT import COVID_CT
from .COVIDChestXRay import COVIDChestXRay
from .DeepRoute import DeepRoute
from .DogsVsCats import DogsVsCats
from .DownsampledImagenet import DownsampledImagenet
from .Elpv import Elpv
from .FLIC import FLIC
from .Flower import Flower17, Flower102
from .FSDD import FSDD
from .HalpeFullBody import HalpeFullBody
from .HardHatWorkers import HardHatWorkers
from .HeadPoseImage import HeadPoseImage
from .ImageEmotion import ImageEmotionAbstract, ImageEmotionArtphoto
from .JHU_CROWD import JHU_CROWD
from .KenyanFood import KenyanFoodOrNonfood, KenyanFoodType
from .KylbergTexture import KylbergTexture
from .LeedsSportsPose import LeedsSportsPose
from .LISATrafficLight import LISATrafficLight
from .LISATrafficSign import LISATrafficSign
from .NeolixOD import NeolixOD
from .Newsgroups20 import Newsgroups20
from .NightOwls import NightOwls
from .nuScenes import nuScenes
from .RP2K import RP2K
from .THCHS30 import THCHS30
from .THUCNews import THUCNews
from .TLR import TLR
from .UAVDT import UAVDT
from .VOC2012ActionClassification import VOC2012ActionClassification
from .VOC2012Detection import VOC2012Detection
from .WIDER_FACE import WIDER_FACE

__all__ = [
    "nuScenes",
    "AADB",
    "AnimalPose5",
    "AnimalPose7",
    "AnimalsWithAttributes2",
    "BioIDFace",
    "BDD100K",
    "BSTLD",
    "CACD",
    "CADC",
    "CarConnection",
    "CCPD",
    "CCPDGreen",
    "CoinImage",
    "COVIDChestXRay",
    "CompCars",
    "DeepRoute",
    "DogsVsCats",
    "DownsampledImagenet",
    "Elpv",
    "FLIC",
    "FSDD",
    "HalpeFullBody",
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
    "LISATrafficSign",
    "LeedsSportsPose",
    "NeolixOD",
    "Newsgroups20",
    "NightOwls",
    "RP2K",
    "THCHS30",
    "THUCNews",
    "TLR",
    "UAVDT",
    "WIDER_FACE",
    "COVID_CT",
    "VOC2012Detection",
    "VOC2012ActionClassification",
]
