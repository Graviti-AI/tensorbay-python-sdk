#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#
# pylint: disable=invalid-name

"""This file defines the BDD100K dataloader."""

import json
import os
from typing import Any, Dict, List

from ...dataset import Data, Dataset
from ...label import Classification, LabeledBox2D
from ...opendataset import _utility

DATASET_NAME = "BDD100K"
_IMAGE_FOLDER = "Images/100k"
_LABELS_FOLDER = "Labels"
_MODES = ("test", "train", "val")


def BDD100K(path: str) -> Dataset:
    """Load BDD100K Dataset to Tensorbay.

    The file structure should be like::

        <path>
            Images/
                100k/
                    test
                    train
                    val
                10k/
                    test
                    train
                    val
            Labels/
                bdd100k_labels_images_train.json
                bdd100k_labels_images_val.json

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    label_path = {
        "train": os.path.join(root_path, _LABELS_FOLDER, "bdd100k_labels_images_train.json"),
        "val": os.path.join(root_path, _LABELS_FOLDER, "bdd100k_labels_images_val.json"),
        "test": "",
    }

    for mode in _MODES:
        _load_segment(
            dataset=dataset,
            path=root_path,
            mode=mode,
            label_file_path=label_path[mode],
        )

    return dataset


def _load_segment(
    dataset: Dataset,
    path: str,
    mode: str,
    label_file_path: str,
) -> None:
    segment = dataset.create_segment(mode)
    segment_path = os.path.join(path, _IMAGE_FOLDER, mode)
    image_paths = _utility.glob(os.path.join(path, _IMAGE_FOLDER, mode, "*.jpg"))
    unlabeled_image_names = []
    if mode == "test":
        for image_path in image_paths:
            segment.append(Data(image_path))
        return

    with open(label_file_path) as fp:
        labels = json.load(fp)

    image_name_to_label = {}
    for label in labels:
        image_name_to_label[label["name"]] = label

    for image_path in image_paths:
        image_name = os.path.basename(image_path)
        if image_name not in image_name_to_label:
            unlabeled_image_names.append(image_name)
            continue

        data = Data(image_path)
        _add_label(data, image_name_to_label[image_name])
        segment.append(data)

    if unlabeled_image_names:
        _load_unlabeled_segment(dataset, unlabeled_image_names, mode, segment_path)


def _load_unlabeled_segment(
    dataset: Dataset, unlabeled_image_names: List[str], mode: str, segment_path: str
) -> None:
    segment = dataset.create_segment(f"unlabeled_images_in_{mode}")
    for unlabeled_image_name in unlabeled_image_names:
        data = Data(os.path.join(segment_path, unlabeled_image_name))
        segment.append(data)


def _add_label(data: Data, labels: Dict[str, Any]) -> None:
    data.label.classification = Classification(attributes=labels["attributes"])
    box2d_labels = []
    for label in labels["labels"]:
        if "box2d" in label:
            box2d_info = label["box2d"]
            box2d_label = LabeledBox2D(
                box2d_info["x1"],
                box2d_info["y1"],
                box2d_info["x2"],
                box2d_info["y2"],
                category=label["category"],
                attributes=label["attributes"],
            )
            box2d_labels.append(box2d_label)

    data.label.box2d = box2d_labels
