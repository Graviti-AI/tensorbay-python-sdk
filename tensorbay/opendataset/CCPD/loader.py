#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name, missing-module-docstring

import os
from typing import Dict, Iterator, List, Union

from ...dataset import Data, Dataset
from ...label import LabeledPolygon
from .._utility.glob import glob

_PROVINCES = (
    "皖",
    "沪",
    "津",
    "渝",
    "冀",
    "晋",
    "蒙",
    "辽",
    "吉",
    "黑",
    "苏",
    "浙",
    "京",
    "闽",
    "赣",
    "鲁",
    "豫",
    "鄂",
    "湘",
    "粤",
    "桂",
    "琼",
    "川",
    "贵",
    "云",
    "藏",
    "陕",
    "甘",
    "青",
    "宁",
    "新",
    "警",
    "学",
)

_CODES = (
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "J",
    "K",
    "L",
    "M",
    "N",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
)

_ADS = (
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "J",
    "K",
    "L",
    "M",
    "N",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
)

_CCPD_SEGMENTS = {
    "other": ("np", "weather"),
    "train": ("base",),
    "val": ("base",),
    "test": ("blur", "challenge", "db", "fn", "rotate", "tilt"),
}

_CCPDGREEN_SEGMENTS = ("train", "val", "test")

DATASET_NAME_CCPD = "CCPD"
DATASET_NAME_CCPDGREEN = "CCPDGreen"


def CCPD(path: str) -> Dataset:
    """Dataloader of CCPD open dataset.

    .. _CCPD: https://github.com/detectRecog/CCPD

    The file structure should be like::

        <path>
            ccpd_np/
                1005.jpg
                1019.jpg
                ...
            ccpd_base/
                00205459770115-90_85-352&516_448&547- \
                444&547_368&549_364&517_440&515-0_0_22_10_26_29_24-128-7.jpg
                00221264367816-91_91-283&519_381&553- \
                375&551_280&552_285&514_380&513-0_0_7_26_17_33_29-95-9.jpg
                ...
            ccpd_blur/
            ccpd_challenge/
            ccpd_db/
            ccpd_fn/
            ccpd_rotate/
            ccpd_tilt/
            ccpd_weather/
            LICENSE
            README.md
            splits/
                ccpd_blur.txt
                ccpd_challenge.txt
                ccpd_db.txt
                ccpd_fn.txt
                ccpd_rotate.txt
                ccpd_tilt.txt
                test.txt
                train.txt
                val.txt

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class: `~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = Dataset(DATASET_NAME_CCPD)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_head, segment_tails in _CCPD_SEGMENTS.items():
        for segment_tail in segment_tails:
            segment_name = f"{segment_head}-{segment_tail}"
            segment = dataset.create_segment(segment_name)
            get_polygons = _get_polygons if segment_name != "other-np" else lambda _: []
            for image_path in _get_ccpd_image_path(root_path, segment_head, segment_tail):
                data = Data(image_path)
                data.label.polygon = get_polygons(image_path)
                segment.append(data)
    return dataset


def CCPDGreen(path: str) -> Dataset:
    """Dataloader of CCPDGreen open dataset.

    .. _CCPD: https://github.com/detectRecog/CCPD

    The file structure should be like::

        <path>
            ccpd_green/
                train/
                test/
                val/

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class: `~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.join(os.path.abspath(os.path.expanduser(path)), "ccpd_green")

    dataset = Dataset(DATASET_NAME_CCPDGREEN)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name in _CCPDGREEN_SEGMENTS:
        segment = dataset.create_segment(segment_name)
        for image_path in glob(os.path.join(root_path, segment_name, "*.jpg")):
            data = Data(image_path)
            data.label.polygon = _get_polygons(image_path)
            segment.append(data)
    return dataset


def _get_license_plate(license_index: str) -> str:
    indexes = map(int, license_index.split("_"))
    return (
        f"{_PROVINCES[next(indexes)]}{_CODES[next(indexes)]}"
        f"{''.join(_ADS[index] for index in indexes)}"
    )


def _get_polygons(image_path: str) -> List[LabeledPolygon]:
    attributes: Dict[str, Union[int, str]] = {}
    annotations = os.path.splitext(os.path.basename(image_path))[0].split("-", 6)
    points = (map(int, point.split("&")) for point in annotations[3].split("_", 3))
    tilt_degree = annotations[1].split("_", 1)
    attributes["horizontal_tilt"] = int(tilt_degree[0])
    attributes["vertical_tilt"] = int(tilt_degree[1])
    attributes["license_plate"] = _get_license_plate(annotations[4])
    attributes["brightness"] = int(annotations[5])
    attributes["blurriness"] = int(annotations[6])
    return [LabeledPolygon(points, attributes=attributes)]


def _get_ccpd_image_path(root_path: str, segment_head: str, segment_tail: str) -> Iterator[str]:
    if segment_tail == "base":
        file_path = os.path.join(root_path, "splits", f"{segment_head}.txt")
        with open(file_path, "r") as fp:
            for image_path in fp:
                yield os.path.join(root_path, image_path.strip())
    else:
        for image_path in glob(os.path.join(root_path, f"ccpd_{segment_tail}", "*.jpg")):
            yield image_path
