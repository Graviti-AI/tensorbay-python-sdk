#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name, missing-module-docstring

import os
from collections import defaultdict
from typing import Callable, DefaultDict, Dict, Tuple

from ...dataset import Data, Dataset
from ...label import Classification

_SEGMENTS_INFO = (
    ("new_test", "AADB_newtest", "imgListTestNewRegression"),
    ("test", "datasetImages_warp256", "imgListTestRegression"),
    ("train", "datasetImages_warp256", "imgListTrainRegression"),
    ("val", "datasetImages_warp256", "imgListValidationRegression"),
)

DATASET_NAME = "AADB"


def AADB(path: str) -> Dataset:
    """Load the AADB to TensorBay.

    The file structure looks like:

        <path>
            AADB_newtest/
                0.500_farm1_487_20167490236_ae920475e2_b.jpg
                ...
            datasetImages_warp256/
                farm1_441_19470426814_baae1eb396_b.jpg
                ...
            imgListFiles_label/
                imgList<segment_name>Regression_<attribute_name>.txt
                ...

    Arguments:
        path: the root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    attribute_names = dataset.catalog.classification.attributes.keys()

    for mode, image_directory, label_file_prefix in _SEGMENTS_INFO:
        image_name_handler: Callable[[str, Dict[str, float]], str] = (
            (lambda image_name, attributes: f"{attributes['score']:.3f}_{image_name}")
            if mode == "new_test"
            else (lambda image_name, _: image_name)
        )

        segment = dataset.create_segment(mode)
        attributes_map = _extract_attributes_map(root_path, label_file_prefix, attribute_names)
        for image_name, attributes in attributes_map.items():
            real_image_name = image_name_handler(image_name, attributes)
            image_path = os.path.join(root_path, image_directory, real_image_name)
            data = Data(image_path)
            data.label.classification = Classification(attributes=attributes)
            segment.append(data)

    return dataset


def _extract_attributes_map(
    path: str, label_file_prefix: str, attribute_names: Tuple[str, ...]
) -> Dict[str, Dict[str, float]]:
    attributes_map: DefaultDict[str, Dict[str, float]] = defaultdict(dict)
    label_directory = os.path.join(path, "imgListFiles_label")
    for attribute_name in attribute_names:
        label_file_name = f"{label_file_prefix}_{attribute_name}.txt"
        label_file_path = os.path.join(label_directory, label_file_name)
        with open(label_file_path) as fp:
            # one line of file looks like:
            # "<image_name> value"
            for line in fp:
                image_name, value = line.strip().split()
                attributes_map[image_name][attribute_name] = float(value)

    return attributes_map
