#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import os
from typing import List
from xml.etree import ElementTree

from ...dataset import Data, Dataset
from ...label import LabeledBox2D
from .._utility import glob

DATASET_NAME = "HardHatWorkers"


def HardHatWorkers(path: str) -> Dataset:
    """Dataloader of the `Hard Hat Workers`_ dataset.

    .. _Hard Hat Workers: https://makeml.app/datasets/hard-hat-workers

    The file structure should be like::

        <path>
            annotations/
                hard_hat_workers0.xml
                ...
            images/
                hard_hat_workers0.png
                ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    segment = dataset.create_segment()
    image_paths = glob(os.path.join(path, "images", "*.png"))
    for image_path in image_paths:
        data = Data(image_path)
        file_name = os.path.splitext(os.path.basename(image_path))[0]
        data.label.box2d = _load_labels(os.path.join(path, "annotations", file_name + ".xml"))
        segment.append(data)
    return dataset


def _load_labels(label_file: str) -> List[LabeledBox2D]:
    label_tree = ElementTree.parse(label_file)
    labels = []
    for obj in label_tree.findall("object"):
        bndbox = obj.find("bndbox")
        labels.append(
            LabeledBox2D(
                *(int(child.text) for child in bndbox),  # type: ignore[arg-type, union-attr]
                category=obj.find("name").text  # type: ignore[union-attr]
            )
        )
    return labels
