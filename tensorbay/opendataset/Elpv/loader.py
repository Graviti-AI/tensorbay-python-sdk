#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#
# pylint: disable=invalid-name

"""This file define the Elpv Dataloader"""

import os

from ...dataset import Data, Dataset
from ...label import Classification

DATASET_NAME = "Elpv"


def Elpv(path: str) -> Dataset:
    """
    Elpv open dataset dataloader
    :param path:Path to Elpv dataset
    the file structure should be like:
    <path>
        labels.csv
        images/
            cell0001.png
            ...

    :return:load `Dataset` object
    """
    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    segment = dataset.create_segment()

    csv_path = os.path.join(root_path, "labels.csv")

    with open(csv_path) as csv_file:
        for row in csv_file:
            image_name, attributes, category = row.strip().split()
            dirname, basename = image_name.split("/")
            image_path = os.path.join(root_path, dirname, basename)
            data = Data(image_path)
            data.labels.classification = Classification(
                attributes={"defect probability": float(attributes)}, category=category
            )
            segment.append(data)
    return dataset
