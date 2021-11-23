#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Common methods for loading VOC formatted datasets."""

import os
from typing import Any, List

from tensorbay.dataset import Data
from tensorbay.label import Box2DSubcatalog, LabeledBox2D

try:
    import xmltodict
except ModuleNotFoundError:
    from tensorbay.opendataset._utility.mocker import xmltodict  # pylint:disable=ungrouped-imports


def get_voc_detection_data(
    stem: str, image_path: str, annotation_path: str, boolean_attributes: List[str]
) -> Data:
    """Get all information of the datum corresponding to voc-like label files.

    Arguments:
        stem: The filename without extension of the data.
        image_path: The path of the image directory.
        annotation_path: The path of the annotation directory.
        boolean_attributes: The list of boolean attribute.

    Returns:
        Data: class:`~tensorbay.dataset.data.Data` instance.

    """
    data = Data(os.path.join(image_path, f"{stem}.jpg"))
    box2d = []
    with open(os.path.join(annotation_path, f"{stem}.xml"), encoding="utf-8") as fp:
        labels: Any = xmltodict.parse(fp.read())
    objects = labels["annotation"]["object"]

    if not isinstance(objects, list):
        objects = [objects]
    for obj in objects:
        attributes = {attribute: bool(int(obj[attribute])) for attribute in boolean_attributes}
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


def get_boolean_attributes(box2d: Box2DSubcatalog) -> List[str]:
    """Get boolean attributes.

    Arguments:
        box2d: The Box2DSubcatalog.

    Returns:
        Iterable: The list of bo olean attribute.
    """
    return [
        attribute.name
        for attribute in box2d.attributes
        if getattr(attribute, "type", None) == "boolean"
    ]
