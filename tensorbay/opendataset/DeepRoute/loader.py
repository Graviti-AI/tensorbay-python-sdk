#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of the DeepRoute dataset."""

import json
import os

from ...dataset import Data, Dataset
from ...label import LabeledBox3D
from .._utility import glob

DATASET_NAME = "DeepRoute"


def DeepRoute(path: str) -> Dataset:
    """Dataloader of the DeepRoute dataset.

    Arguments:
        path: The root directory of the dataset.
            The file structure should be like::

                <path>
                    pointcloud/
                        00001.bin
                        00002.bin
                        ...
                        10000.bin
                    groundtruth/
                        00001.txt
                        00002.txt
                        ...
                        10000.txt

    Returns:
        Loaded `Dataset` object.

    """
    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    segment = dataset.create_segment()

    point_cloud_paths = glob(os.path.join(root_path, "pointcloud", "*.bin"))

    for point_cloud_path in point_cloud_paths:
        point_cloud_id = os.path.splitext(os.path.basename(point_cloud_path))[0]
        label_path = os.path.join(root_path, "groundtruth", f"{point_cloud_id}.txt")

        data = Data(point_cloud_path)
        data.label.box3d = []

        with open(label_path) as fp:
            annotations = json.load(fp)["objects"]

        for annotation in annotations:
            bounding_box = annotation["bounding_box"]
            position = annotation["position"]

            label = LabeledBox3D(
                category=annotation["type"],
                size=(bounding_box["length"], bounding_box["width"], bounding_box["height"]),
                translation=(position["x"], position["y"], position["z"]),
                axis=(0, 0, 1),
                radians=annotation["heading"],
            )
            data.label.box3d.append(label)

        segment.append(data)

    return dataset
