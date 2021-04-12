#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import json
import os
from typing import Any, Dict, Optional

from ...dataset import Data, Dataset
from ...label import LabeledBox2D
from .._utility import coco, glob

DATASET_NAME = "NightOwls"


def NightOwls(path: str) -> Dataset:
    """Dataloader of the `NightOwls`_ dataset.

    .. _NightOwls: http://www.nightowls-dataset.org/

    The file structure should be like::

        <path>
            nightowls_test/
                <image_name>.png
                ...
            nightowls_training/
                <image_name>.png
                ...
            nightowls_validation/
                <image_name>.png
                ...
            nightowls_training.json
            nightowls_validation.json

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = Dataset(DATASET_NAME)
    dataset.notes.is_continuous = True
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for mode, (labels_filename, labels_handler) in _LABELS_HANDEL_METHODS.items():
        segment = dataset.create_segment(mode)

        image_paths = glob(os.path.join(root_path, f"nightowls_{mode}", "*.png"))

        labels = _load_labels(root_path, labels_filename)

        for image_path in image_paths:
            data = labels_handler(image_path, labels)  # pylint: disable=not-callable
            segment.append(data)

    return dataset


def _load_labels(root_path: str, labels_filename: Optional[str]) -> Dict[str, Any]:
    if not labels_filename:
        return {"test": None}

    label_path = os.path.join(root_path, labels_filename)
    with open(label_path, "r", encoding="utf-8") as fp:
        loaded_data = json.load(fp)

    labels = {}

    image_name_id_map = {image["file_name"]: image["id"] for image in loaded_data["images"]}
    labels["image_name_id_map"] = image_name_id_map
    labels["poses"] = loaded_data["poses"]

    # the origin name of forth pose is "nan", this expression changes it to None
    labels["poses"][4]["name"] = None

    coco_labels = coco(os.path.join(root_path, labels_filename))

    labels["images"] = coco_labels.images
    labels["annotations"] = coco_labels.annotations
    labels["image_annotations_map"] = coco_labels.image_annotations_map
    labels["categories"] = coco_labels.categories

    return labels


def _generate_data(image_path: str, labels: Dict[str, Any]) -> Data:
    data = Data(image_path)
    data.label.box2d = []

    image_id = labels["image_name_id_map"][os.path.basename(image_path)]
    image_annotations_map = labels["image_annotations_map"]

    if image_id not in image_annotations_map:
        return data

    annotations = labels["annotations"]
    poses = labels["poses"]
    categories = labels["categories"]

    for annotation_id in image_annotations_map[image_id]:
        annotation = annotations[annotation_id]
        x_top, y_top, width, height = annotation["bbox"]

        attributes = {
            "occluded": annotation["occluded"],
            "difficult": annotation["difficult"],
            "pose": poses[annotation["pose_id"] - 1]["name"],
            "truncated": annotation["truncated"],
        }

        data.label.box2d.append(
            LabeledBox2D.from_xywh(
                x=x_top,
                y=y_top,
                width=width,
                height=height,
                category=categories[annotation["category_id"]]["name"],
                attributes=attributes,
                instance=str(annotation["tracking_id"]),
            )
        )

    return data


_LABELS_HANDEL_METHODS = {
    "training": ("nightowls_training.json", _generate_data),
    "validation": ("nightowls_validation.json", _generate_data),
    "test": (None, lambda image_path, _: Data(image_path)),
}
