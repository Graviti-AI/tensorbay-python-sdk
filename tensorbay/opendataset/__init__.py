#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""OpenDataset dataloader collections."""

from .AADB import AADB
from .AnimalPose import AnimalPose5, AnimalPose7
from .AnimalsWithAttributes2 import AnimalsWithAttributes2
from .BDD100K import BDD100K, BDD100K_10K
from .BDD100K_MOT2020 import BDD100K_MOT2020, BDD100K_MOTS2020
from .BioIDFace import BioIDFace
from .BSTLD import BSTLD
from .CACD import CACD
from .CADC import CADC
from .CarConnection import CarConnection
from .CCPD import CCPD, CCPDGreen
from .CIHP import CIHP
from .COCO2017 import COCO2017
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
from .LIP import LIP
from .LISATrafficLight import LISATrafficLight
from .LISATrafficSign import LISATrafficSign
from .NeolixOD import NeolixOD
from .Newsgroups20 import Newsgroups20
from .NightOwls import NightOwls
from .nuImages import nuImages
from .nuScenes import nuScenes
from .OxfordIIITPet import OxfordIIITPet
from .PASCALContext import PASCALContext
from .RP2K import RP2K
from .SegTrack import SegTrack
from .SegTrack2 import SegTrack2
from .SVHN import SVHN
from .THCHS30 import THCHS30
from .THUCNews import THUCNews
from .TLR import TLR
from .UAVDT import UAVDT
from .VOC2012ActionClassification import VOC2012ActionClassification
from .VOC2012Detection import VOC2012Detection
from .VOC2012Segmentation import VOC2012Segmentation
from .WIDER_FACE import WIDER_FACE

__all__ = [
    "nuScenes",
    "AADB",
    "AnimalPose5",
    "AnimalPose7",
    "AnimalsWithAttributes2",
    "BioIDFace",
    "BDD100K",
    "BDD100K_MOT2020",
    "BDD100K_MOTS2020",
    "BDD100K_10K",
    "BSTLD",
    "CACD",
    "CADC",
    "CarConnection",
    "CCPD",
    "CCPDGreen",
    "CIHP",
    "COCO2017",
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
    "LIP",
    "LISATrafficLight",
    "LISATrafficSign",
    "LeedsSportsPose",
    "NeolixOD",
    "Newsgroups20",
    "NightOwls",
    "OxfordIIITPet",
    "PASCALContext",
    "RP2K",
    "SegTrack",
    "SegTrack2",
    "SVHN",
    "nuImages",
    "THCHS30",
    "THUCNews",
    "TLR",
    "UAVDT",
    "WIDER_FACE",
    "COVID_CT",
    "VOC2012Detection",
    "VOC2012ActionClassification",
    "VOC2012Segmentation",
]
