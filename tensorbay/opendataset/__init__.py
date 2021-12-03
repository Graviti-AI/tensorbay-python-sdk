#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""OpenDataset dataloader collections."""

from tensorbay.opendataset.AADB import AADB
from tensorbay.opendataset.AnimalPose import AnimalPose5, AnimalPose7
from tensorbay.opendataset.AnimalsWithAttributes2 import AnimalsWithAttributes2
from tensorbay.opendataset.BDD100K import BDD100K, BDD100K_10K
from tensorbay.opendataset.BDD100K_MOT2020 import BDD100K_MOT2020, BDD100K_MOTS2020
from tensorbay.opendataset.BioIDFace import BioIDFace
from tensorbay.opendataset.BSTLD import BSTLD
from tensorbay.opendataset.CACD import CACD
from tensorbay.opendataset.CADC import CADC
from tensorbay.opendataset.CarConnection import CarConnection
from tensorbay.opendataset.CCPD import CCPD, CCPDGreen
from tensorbay.opendataset.CIHP import CIHP
from tensorbay.opendataset.Cityscapes import CityscapesGTCoarse, CityscapesGTFine
from tensorbay.opendataset.COCO2017 import COCO2017
from tensorbay.opendataset.CoinImage import CoinImage
from tensorbay.opendataset.CompCars import CompCars
from tensorbay.opendataset.COVID_CT import COVID_CT
from tensorbay.opendataset.COVIDChestXRay import COVIDChestXRay
from tensorbay.opendataset.DAVIS2017 import DAVIS2017SemiSupervised, DAVIS2017Unsupervised
from tensorbay.opendataset.DeepRoute import DeepRoute
from tensorbay.opendataset.DogsVsCats import DogsVsCats
from tensorbay.opendataset.DownsampledImagenet import DownsampledImagenet
from tensorbay.opendataset.Elpv import Elpv
from tensorbay.opendataset.FLIC import FLIC
from tensorbay.opendataset.Flower import Flower17, Flower102
from tensorbay.opendataset.FSDD import FSDD
from tensorbay.opendataset.HalpeFullBody import HalpeFullBody
from tensorbay.opendataset.HardHatWorkers import HardHatWorkers
from tensorbay.opendataset.HeadPoseImage import HeadPoseImage
from tensorbay.opendataset.ImageEmotion import ImageEmotionAbstract, ImageEmotionArtphoto
from tensorbay.opendataset.JHU_CROWD import JHU_CROWD
from tensorbay.opendataset.KenyanFood import KenyanFoodOrNonfood, KenyanFoodType
from tensorbay.opendataset.KylbergTexture import KylbergTexture
from tensorbay.opendataset.LeedsSportsPose import LeedsSportsPose
from tensorbay.opendataset.LIP import LIP
from tensorbay.opendataset.LISATrafficLight import LISATrafficLight
from tensorbay.opendataset.LISATrafficSign import LISATrafficSign
from tensorbay.opendataset.NeolixOD import NeolixOD
from tensorbay.opendataset.Newsgroups20 import Newsgroups20
from tensorbay.opendataset.NightOwls import NightOwls
from tensorbay.opendataset.nuImages import nuImages
from tensorbay.opendataset.nuScenes import nuScenes
from tensorbay.opendataset.OxfordIIITPet import OxfordIIITPet
from tensorbay.opendataset.PASCALContext import PASCALContext
from tensorbay.opendataset.RarePlanesReal import RarePlanesReal
from tensorbay.opendataset.RarePlanesSynthetic import RarePlanesSynthetic
from tensorbay.opendataset.RP2K import RP2K
from tensorbay.opendataset.SCUT_FBP5500 import SCUT_FBP5500
from tensorbay.opendataset.SegTrack import SegTrack
from tensorbay.opendataset.SegTrack2 import SegTrack2
from tensorbay.opendataset.SVHN import SVHN
from tensorbay.opendataset.THCHS30 import THCHS30
from tensorbay.opendataset.THUCNews import THUCNews
from tensorbay.opendataset.TLR import TLR
from tensorbay.opendataset.UAVDT import UAVDT
from tensorbay.opendataset.UrbanObjectDetection import UrbanObjectDetection
from tensorbay.opendataset.VGGFace2 import VGGFace2
from tensorbay.opendataset.VOC2012ActionClassification import VOC2012ActionClassification
from tensorbay.opendataset.VOC2012Detection import VOC2012Detection
from tensorbay.opendataset.VOC2012Segmentation import VOC2012Segmentation
from tensorbay.opendataset.WIDER_FACE import WIDER_FACE

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
    "CityscapesGTCoarse",
    "CityscapesGTFine",
    "COCO2017",
    "CoinImage",
    "COVIDChestXRay",
    "CompCars",
    "DAVIS2017SemiSupervised",
    "DAVIS2017Unsupervised",
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
    "RarePlanesReal",
    "RarePlanesSynthetic",
    "RP2K",
    "SCUT_FBP5500",
    "SegTrack",
    "SegTrack2",
    "SVHN",
    "nuImages",
    "THCHS30",
    "THUCNews",
    "TLR",
    "UAVDT",
    "UrbanObjectDetection",
    "WIDER_FACE",
    "COVID_CT",
    "VGGFace2",
    "VOC2012Detection",
    "VOC2012ActionClassification",
    "VOC2012Segmentation",
]
