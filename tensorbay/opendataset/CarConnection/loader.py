#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

import os
from typing import Tuple, Union

from ...dataset import Data, Dataset
from ...label import Classification
from .._utility import glob

DATASET_NAME = "CarConnectionPicture"


def CarConnection(path: str) -> Dataset:
    """Dataloader of `The Car Connection Picture`_ dataset.

    .. _The Car Connection Picture: https://github.com/nicolas-gervais/predicting-car-price-from-scraped-data/tree/master/picture-scraper # noqa: E501

    The file structure should be like::

        <path>
            <imagename>.jpg
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

    image_paths = glob(os.path.join(root_path, "*.jpg"))
    keys = dataset.catalog.classification.attributes.keys()

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


def _extract_label_from_basename(keys: Tuple[str, ...], filename: str) -> Classification:
    make, model, *spec_values = filename.split("_")[:-1]

    attributes = dict(zip(keys, map(_transfer_attribute_type, spec_values)))

    category = ".".join((make, model))

    return Classification(attributes=attributes, category=category)
