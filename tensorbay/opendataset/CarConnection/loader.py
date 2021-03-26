#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of the The Car Connection Picture dataset."""

import os
from typing import Union

from ...dataset import Data, Dataset
from ...label import AttributeInfo, Classification
from ...utility import NameOrderedDict
from .._utility import glob

DATASET_NAME = "The Car Connection Picture"


def CarConnection(path: str) -> Dataset:
    """Dataloader of the The Car Connection Picture dataset.

    Arguments:
        path: The root directory of the dataset.
            The file structure should be like::

                <path>
                    <imagename>.jpg
                    ...

    Returns:
        Loaded `Dataset` object.

    """
    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    segment = dataset.create_segment()

    image_paths = glob(os.path.join(root_path, "*.jpg"))
    keys = dataset.catalog.classification.attributes

    for image_path in image_paths:
        data = Data(image_path)
        basename = os.path.basename(image_path)
        label = _extract_label_from_basename(keys, basename)
        data.label.classification = label
        segment.append(data)

    return dataset


def _transfer_attribute_type(item: str) -> Union[int, str, None]:
    if item == "nan":
        return None
    if item.isnumeric():
        return int(item)

    return item


def _extract_label_from_basename(
    keys: NameOrderedDict[AttributeInfo], filename: str
) -> Classification:
    make, model, *spec_values = filename.split("_")[:-1]

    attributes = dict(zip(keys, map(_transfer_attribute_type, spec_values)))

    category = ".".join((make, model))

    return Classification(attributes=attributes, category=category)
