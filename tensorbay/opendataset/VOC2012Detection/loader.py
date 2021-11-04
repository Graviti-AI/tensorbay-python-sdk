#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name, missing-module-docstring

import os

from tensorbay.dataset import Data, Dataset
from tensorbay.label import LabeledBox2D

try:
    import xmltodict
except ModuleNotFoundError:
    from tensorbay.opendataset._utility.mocker import xmltodict  # pylint:disable=ungrouped-imports

_SEGMENT_NAMES = ("train", "val")
_BOOLEAN_ATTRIBUTES = {"occluded", "difficult", "truncated"}
DATASET_NAME = "VOC2012Detection"


def VOC2012Detection(path: str) -> Dataset:
    """`VOC2012Detection <http://host.robots.ox.ac.uk/pascal/VOC/voc2012/>`_ dataset.

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
    main_path = os.path.join(root_path, "ImageSets", "Main")

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name in _SEGMENT_NAMES:
        segment = dataset.create_segment(segment_name)
        with open(os.path.join(main_path, f"{segment_name}.txt"), encoding="utf-8") as fp:
            for filename in fp:
                segment.append(_get_data(filename.rstrip(), image_path, annotation_path))
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
    box2d = []
    with open(os.path.join(annotation_path, f"{filename}.xml"), "r", encoding="utf-8") as fp:
        objects = xmltodict.parse(fp.read())["annotation"]["object"]
    if not isinstance(objects, list):
        objects = [objects]
    for obj in objects:
        attributes = {attribute: bool(int(obj[attribute])) for attribute in _BOOLEAN_ATTRIBUTES}
        attributes["pose"] = obj["pose"]
        bndbox = obj["bndbox"]
        box2d.append(
            LabeledBox2D(
                float(bndbox["xmin"]),
                float(bndbox["ymin"]),
                float(bndbox["xmax"]),
                float(bndbox["ymax"]),
                category=obj["name"],
                attributes=attributes,
            )
        )
    data.label.box2d = box2d
    return data
