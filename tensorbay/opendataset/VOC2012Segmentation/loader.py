#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of VOC2012Segmentation dataset."""

import os

from tensorbay.dataset import Data, Dataset
from tensorbay.label import InstanceMask, SemanticMask

_SEGMENT_NAMES = ("train", "val")
DATASET_NAME = "VOC2012Segmentation"


def VOC2012Segmentation(path: str) -> Dataset:
    """`VOC2012Segmentation <http://host.robots.ox.ac.uk/pascal/VOC/voc2012/>`_ dataset.

    The file structure should be like::

        <path>/
            JPEGImages/
                <image_name>.jpg
                ...
            SegmentationClass/
                <mask_name>.png
                ...
            SegmentationObject/
                <mask_name>.png
                ...
            ImageSets/
                Segmentation/
                    train.txt
                    val.txt
                    ...
                ...
            ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class: `~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))

    image_path = os.path.join(root_path, "JPEGImages")
    semantic_mask_path = os.path.join(root_path, "SegmentationClass")
    instance_mask_path = os.path.join(root_path, "SegmentationObject")
    image_set_path = os.path.join(root_path, "ImageSets", "Segmentation")

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name in _SEGMENT_NAMES:
        segment = dataset.create_segment(segment_name)
        with open(os.path.join(image_set_path, f"{segment_name}.txt"), encoding="utf-8") as fp:
            for stem in fp:
                stem = stem.strip()
                data = Data(os.path.join(image_path, f"{stem}.jpg"))
                label = data.label
                mask_filename = f"{stem}.png"
                label.semantic_mask = SemanticMask(os.path.join(semantic_mask_path, mask_filename))
                label.instance_mask = InstanceMask(os.path.join(instance_mask_path, mask_filename))

                segment.append(data)

    return dataset
