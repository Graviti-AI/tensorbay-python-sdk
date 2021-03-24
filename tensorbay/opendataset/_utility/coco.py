#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Coco method for open dataset."""

import json
from collections import defaultdict
from typing import Any, Dict, List, NamedTuple


class COCO(NamedTuple):
    """This class stores processed coco annotations."""

    images: Dict[int, Dict[str, Any]]
    annotations: Dict[int, Dict[str, Any]]
    categories: Dict[int, Dict[str, Any]]
    image_annotations_map: Dict[int, List[int]]


def _generate_image_annotations_map(dataset: Dict[str, Any]) -> Dict[int, List[int]]:
    image_annotations_map = defaultdict(list)
    for annotation in dataset["annotations"]:
        image_annotations_map[annotation["image_id"]].append(annotation["id"])
    return image_annotations_map


def coco(path: str) -> COCO:
    """Parse the coco-like label files.

    Arguments:
        path: The label directory of the dataset.

    Returns:
        A dict containing four dicts::

            ======================  =============  ==========================
            dicts                   keys           values
            ======================  =============  ==========================
            images                  image id       information of image files
            annotations             annotation id  annotations
            categories              category id    all categories
            images_annotations_map  image id       annotation id
            ======================  =============  ==========================

    """
    with open(path, "r", encoding="utf-8") as fp:
        info = json.load(fp)

    images = {image["id"]: image for image in info["images"]}
    annotations = {annotation["id"]: annotation for annotation in info["annotations"]}
    categories = {category["id"]: category for category in info["categories"]}

    image_annotations_map = _generate_image_annotations_map(info)

    return COCO(images, annotations, categories, image_annotations_map)
