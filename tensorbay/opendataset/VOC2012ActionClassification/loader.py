#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of VOC2012ActionClassification dataset."""

import os
from typing import Any

from tensorbay.dataset import Data, Dataset
from tensorbay.exception import ModuleImportError
from tensorbay.label import LabeledBox2D

_SEGMENT_NAMES = ("train", "val")
DATASET_NAME = "VOC2012ActionClassification"


def VOC2012ActionClassification(path: str) -> Dataset:
    """`VOC2012ActionClassification <http://host.robots.ox.ac.uk/pascal/VOC/voc2012/>`_ dataset.

    The file structure should be like::

        <path>
            Annotations/
                <image_name>.xml
                ...
            JPEGImages/
                <image_name>.jpg
                ...
            ImageSets/
                Action/
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
    annotation_path = os.path.join(root_path, "Annotations")
    image_path = os.path.join(root_path, "JPEGImages")
    action_path = os.path.join(root_path, "ImageSets", "Action")

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name in _SEGMENT_NAMES:
        segment = dataset.create_segment(segment_name)
        with open(os.path.join(action_path, f"{segment_name}.txt"), encoding="utf-8") as fp:
            for stem in fp:
                stem = stem.strip()
                segment.append(_get_data(stem, image_path, annotation_path))
    return dataset


def _get_data(stem: str, image_path: str, annotation_path: str) -> Data:
    try:
        import xmltodict  # pylint: disable=import-outside-toplevel
    except ModuleNotFoundError as error:
        raise ModuleImportError(module_name=error.name) from error
    data = Data(os.path.join(image_path, f"{stem}.jpg"))
    box2d = []
    with open(os.path.join(annotation_path, f"{stem}.xml"), encoding="utf-8") as fp:
        labels: Any = xmltodict.parse(fp.read())
    objects = labels["annotation"]["object"]

    if not isinstance(objects, list):
        objects = [objects]
    for item in objects:
        category = item["name"]
        attributes = {k: bool(int(v)) for k, v in item["actions"].items()}
        bndbox = item["bndbox"]
        box2d.append(
            LabeledBox2D(
                float(bndbox["xmin"]),
                float(bndbox["ymin"]),
                float(bndbox["xmax"]),
                float(bndbox["ymax"]),
                category=category,
                attributes=attributes,
            )
        )
    data.label.box2d = box2d
    return data
