#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of HardHatWorker dataset."""

import os
from typing import Any, List

from tensorbay.dataset import Data, Dataset
from tensorbay.label import LabeledBox2D
from tensorbay.opendataset._utility import glob

try:
    import xmltodict
except ModuleNotFoundError:
    from tensorbay.opendataset._utility.mocker import xmltodict  # pylint:disable=ungrouped-imports

DATASET_NAME = "HardHatWorkers"


def HardHatWorkers(path: str) -> Dataset:
    """`Hard Hat Workers <https://makeml.app/datasets/hard-hat-workers>`_ dataset.

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
    root_path = os.path.abspath(os.path.expanduser(path))
    annotation_dir = os.path.join(root_path, "annotations")

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    segment = dataset.create_segment()
    image_paths = glob(os.path.join(root_path, "images", "*.png"))
    for image_path in image_paths:
        data = Data(image_path)
        data.label.box2d = _load_labels(
            os.path.join(annotation_dir, f"{os.path.splitext(os.path.basename(image_path))[0]}.xml")
        )
        segment.append(data)
    return dataset


def _load_labels(label_file: str) -> List[LabeledBox2D]:
    with open(label_file, encoding="utf-8") as fp:
        labels: Any = xmltodict.parse(fp.read())

    objects = labels["annotation"]["object"]
    box2ds = []
    if not isinstance(objects, list):
        objects = [objects]
    for obj in objects:
        bndbox = obj["bndbox"]
        box2ds.append(
            LabeledBox2D(
                xmin=float(bndbox["xmin"]),
                ymin=float(bndbox["ymin"]),
                xmax=float(bndbox["xmax"]),
                ymax=float(bndbox["ymax"]),
                category=obj["name"],
            )
        )
    return box2ds
