#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#
# pylint: disable=invalid-name

"""This file defines the coco method for open dataset"""

import json
from collections import defaultdict
from typing import Any, Dict, List, NamedTuple


class COCO(NamedTuple):
    """
    This class stores processed coco annotations
    """

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
    """
    Parse the coco-like label files.
    :param path: the absolute path of label file of dataset
    :return: a dict contains four dicts:
             "images" contains information of image files, its key is image id
             "annotations" contains annotations, its key is annotation id
             "categories" contains all categories, its key is category id
             "images_annotations_map" is a map from image id to annotation id
    """
    with open(path, "r") as fp:
        info = json.load(fp)

    images = {image["id"]: image for image in info["images"]}
    annotations = {annotation["id"]: annotation for annotation in info["annotations"]}
    categories = {category["id"]: category for category in info["categories"]}

    image_annotations_map = _generate_image_annotations_map(info)

    return COCO(images, annotations, categories, image_annotations_map)
