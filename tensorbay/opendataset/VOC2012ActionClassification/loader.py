#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name, missing-module-docstring

import os

from ...dataset import Data, Dataset
from ...exception import ModuleImportError
from ...label import LabeledBox2D

_SEGMENT_NAMES = (
    "train",
    "trainval",
    "val",
)
DATASET_NAME = "VOC2012ActionClassification"


def VOC2012ActionClassification(path: str) -> Dataset:
    """Dataloader of the 'VOC2012ActionClassification'_ dataset.

    .. _VOC2012ActionClassification: http://host.robots.ox.ac.uk/pascal/VOC/voc2012/

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
                    trainval.txt
                    val.txt
                    ...
                ...
            ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class: `~tensorbay.dataset.dataset.Dataset` instance.

    """
    annotation_path = os.path.join(path, "Annotations")
    image_path = os.path.join(path, "JPEGImages")
    action_path = os.path.join(path, "ImageSets", "Action")

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name in _SEGMENT_NAMES:
        segment = dataset.create_segment(segment_name)
        with open(os.path.join(action_path, f"{segment_name}.txt")) as fp:
            for filename in fp:
                filename = filename.strip()
                segment.append(_get_data(filename, image_path, annotation_path))
    return dataset


def _get_data(filename: str, image_path: str, annotation_path: str) -> Data:
    try:
        import xmltodict  # pylint: disable=import-outside-toplevel
    except ModuleNotFoundError as error:
        raise ModuleImportError(error.name) from error  # type: ignore[arg-type]

    data = Data(os.path.join(image_path, f"{filename}.jpg"))
    box2d = []
    with open(os.path.join(annotation_path, f"{filename}.xml"), "r") as fp:
        objects = xmltodict.parse(fp.read())["annotation"]["object"]
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
