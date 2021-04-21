#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import os

from ...dataset import Data, Dataset
from ...label import Classification
from .._utility import glob

DATASET_NAME = "AnimalsWithAttributes2"


def AnimalsWithAttributes2(path: str) -> Dataset:
    """Dataloader of the `Animals with attributes 2`_ dataset.

    .. _Animals with attributes 2: https://cvml.ist.ac.at/AwA2/

    The file structure should be like::

        <path>
            classes.txt
            predicates.txt
            predicate-matrix-binary.txt
            JPEGImages/
                <classname>/
                    <imagename>.jpg
                ...
            ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    segment = dataset.create_segment()

    with open(os.path.join(root_path, "classes.txt"), encoding="utf-8") as fp:
        class_names = [line[:-1].split("\t", 1)[-1] for line in fp]

    with open(os.path.join(root_path, "predicates.txt"), encoding="utf-8") as fp:
        attribute_keys = [line[:-1].split("\t", 1)[-1] for line in fp]

    with open(os.path.join(root_path, "predicate-matrix-binary.txt"), encoding="utf-8") as fp:
        attribute_values = [line[:-1].split(" ") for line in fp]

    attribute_mapping = {}
    for class_name, values in zip(class_names, attribute_values):
        attribute_mapping[class_name] = Classification(
            category=class_name,
            attributes=dict(zip(attribute_keys, (bool(int(value)) for value in values))),
        )

    for class_name in sorted(os.listdir(os.path.join(root_path, "JPEGImages"))):
        image_paths = glob(os.path.join(root_path, "JPEGImages", class_name, "*.jpg"))
        label = attribute_mapping[class_name]
        for image_path in image_paths:
            data = Data(image_path)
            data.label.classification = label
            segment.append(data)

    return dataset
