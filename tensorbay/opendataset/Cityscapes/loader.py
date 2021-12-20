#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloaders of the CityscapesGTCoarse dataset and the CityscapesGTFine dataset."""

import json
import os
from glob import glob
from typing import List

from tensorbay.dataset import Data, Dataset
from tensorbay.label import InstanceMask, LabeledPolygon, SemanticMask

DATASET_NAME_GTCOARSE = "CityscapesGTCoarse"
DATASET_NAME_GTFINE = "CityscapesGTFine"

_SEGMENT_NAMES_GTCOARSE = ("train", "train_extra", "val")
_SEGMENT_NAMES_GTFINE = ("train", "test", "val")


def CityscapesGTCoarse(path: str) -> Dataset:
    """`CityscapesGTCoarse <https://www.cityscapes-dataset.com/>`_ dataset.

    The file structure should be like::

        <path>
            leftImg8bit/
                train/
                    aachen/
                        aachen_000000_000019_leftImg8bit.png
                        ...
                    ...
                train_extra/
                    augsburg/
                        augsburg_000000_000019_leftImg8bit.png
                        ...
                    ...
                val/
                    frankfurt/
                        frankfurt_000000_000019_leftImg8bit.png
                        ...
                    ...
                ...
            gtCoarse/
                train/
                    aachen/
                        aachen_000000_000019_gtCoarse_instanceIds.png
                        aachen_000000_000019_gtCoarse_labelIds.png
                        aachen_000000_000019_gtCoarse_polygons.json
                        ...
                    ...
                train_extra/
                    augsburg/
                        augsburg_000000_000019_gtCoarse_instanceIds.png
                        augsburg_000000_000019_gtCoarse_labelIds.png
                        augsburg_000000_000019_gtCoarse_polygons.json
                        ...
                    ...
                val/
                    frankfurt/
                        frankfurt_000000_000019_gtCoarse_instanceIds.png
                        frankfurt_000000_000019_gtCoarse_labelIds.png
                        frankfurt_000000_000019_gtCoarse_polygons.json
                        ...
                    ...
            ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.join(os.path.abspath(os.path.expanduser(path)))

    dataset = Dataset(DATASET_NAME_GTCOARSE)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name in _SEGMENT_NAMES_GTCOARSE:
        segment = dataset.create_segment(segment_name)
        for image_path in glob(os.path.join(root_path, "leftImg8bit", segment_name, "*", "*.png")):
            segment.append(_get_data(image_path, root_path, segment_name, "gtCoarse"))
    return dataset


def CityscapesGTFine(path: str) -> Dataset:
    """`CityscapesGTFine <https://www.cityscapes-dataset.com/>`_ dataset.

    The file structure should be like::

        <path>
            leftImg8bit/
                test/
                    berlin/
                        berlin_000000_000019_leftImg8bit.png
                        ...
                    ...
                train/
                    aachen/
                        aachen_000000_000019_leftImg8bit.png
                        ...
                    ...
                val/
                    frankfurt/
                        frankfurt_000000_000019_leftImg8bit.png
                        ...
                    ...
                ...
            gtFine/
                test/
                    berlin/
                        berlin_000000_000019_gtFine_instanceIds.png
                        berlin_000000_000019_gtFine_labelIds.png
                        berlin_000000_000019_gtFine_polygons.json
                        ...
                    ...
                train/
                    aachen/
                        aachen_000000_000019_gtFine_instanceIds.png
                        aachen_000000_000019_gtFine_labelIds.png
                        aachen_000000_000019_gtFine_polygons.json
                        ...
                    ...
                val/
                    frankfurt/
                        frankfurt_000000_000019_gtFine_instanceIds.png
                        frankfurt_000000_000019_gtFine_labelIds.png
                        frankfurt_000000_000019_gtFine_polygons.json
                        ...
                    ...
            ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.join(os.path.abspath(os.path.expanduser(path)))

    dataset = Dataset(DATASET_NAME_GTFINE)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name in _SEGMENT_NAMES_GTFINE:
        segment = dataset.create_segment(segment_name)
        for image_path in glob(os.path.join(root_path, "leftImg8bit", segment_name, "*", "*.png")):
            segment.append(_get_data(image_path, root_path, segment_name, "gtFine"))
    return dataset


def _get_data(image_path: str, root_path: str, segment_name: str, folder_name: str) -> Data:
    filename = os.path.basename(image_path)
    city = filename.split("_", 1)[0]
    image_prefix = filename.rsplit("_", 1)[0]
    label_dir = os.path.join(root_path, folder_name, segment_name, city)
    data = Data(image_path)
    # get semantic mask and instance mask
    label = data.label
    label.semantic_mask = SemanticMask(
        os.path.join(label_dir, f"{image_prefix}_{folder_name}_labelIds.png")
    )
    label.instance_mask = InstanceMask(
        os.path.join(label_dir, f"{image_prefix}_{folder_name}_instanceIds.png")
    )
    # get polygons
    polygons: List[LabeledPolygon] = []
    with open(
        os.path.join(label_dir, f"{image_prefix}_{folder_name}_polygons.json"),
        encoding="utf-8",
    ) as fp:
        objects = json.load(fp)["objects"]
    for obj in objects:
        polygons.append(LabeledPolygon(obj["polygon"], category=obj["label"]))
    label.polygon = polygons

    return data
