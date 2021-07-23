#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name, missing-module-docstring

import os
from xml.etree import ElementTree

from ...dataset import Data, Dataset
from ...label import LabeledBox2D

_SEGMENT_NAMES = (
    "train",
    "trainval",
    "val",
)
_BOOLEAN_ATTRIBUTES = {"occluded", "pose", "truncated"}
DATASET_NAME = "VOC2012Detection"


def VOC2012Detection(path: str) -> Dataset:
    """Dataloader of the 'VOC2012Detection'_ dataset.

    .. _VOC2012Detection: http://host.robots.ox.ac.uk/pascal/VOC/voc2012/

    The file structure should be like::

        <path>
            Annotations/
                <image_name>.xml
                ...
            JPEGImages/
                <image_name>.jpg
                ...
            ImageSets/
                Main/
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
    main_path = os.path.join(path, "ImageSets", "Main")

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name in _SEGMENT_NAMES:
        segment = dataset.create_segment(segment_name)
        with open(os.path.join(main_path, f"{segment_name}.txt")) as fp:
            for filename in fp:
                filename = filename.strip()
                segment.append(_get_data(filename, image_path, annotation_path))
    return dataset


def _get_data(filename: str, image_path: str, annotation_path: str) -> Data:
    """Get all information of the datum corresponding to filename.

    Arguments:
        filename: The filename of the data.
        image_path: The path of the image directory.
        annotation_path: The path of the annotation directory.

    Returns:
        Data: class: `~tensorbay.dataset.data.Data` instance.

    """
    data = Data(os.path.join(image_path, f"{filename}.jpg"))
    data.label.box2d = []
    tree = ElementTree.parse(os.path.join(annotation_path, f"{filename}.xml"))
    for obj in tree.findall("object"):
        attributes = {}
        for child in obj:
            if child.tag == "name":
                category = child.text
            elif child.tag == "bndbox":
                box = (
                    float(child.find("xmin").text),  # type:ignore[arg-type, union-attr]
                    float(child.find("ymin").text),  # type:ignore[arg-type, union-attr]
                    float(child.find("xmax").text),  # type:ignore[arg-type, union-attr]
                    float(child.find("ymax").text),  # type:ignore[arg-type, union-attr]
                )
            elif child.tag == "pose":
                attributes[child.tag] = child.text
            elif child.tag in _BOOLEAN_ATTRIBUTES:
                attributes[child.tag] = bool(
                    int(child.text)  # type:ignore[assignment, arg-type]
                )
        data.label.box2d.append(LabeledBox2D(*box, category=category, attributes=attributes))
    return data
