#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import csv
import os
from typing import Any, Dict

from ...dataset import Data, Dataset
from ...label import Classification

DATASET_NAME = "COVID-chestxray"

_INTEGER_GROUP = {"offset", "age"}
_FLOAT_GROUP = {
    "temperature",
    "pO2_saturation",
    "leukocyte_count",
    "neutrophil_count",
    "lymphocyte_count",
}


def COVIDChestXRay(path: str) -> Dataset:
    """Dataloader of `COVID-chestxray`_ Dataset.

    .. _COVID-chestxray: https://github.com/ieee8023/covid-chestxray-dataset

    The file structure should be like::

        <path>
            images/
                0a7faa2a.jpg
                000001-2.png
                000001-3.jpg
                1B734A89-A1BF-49A8-A1D3-66FAFA4FAC5D.jpeg
                ...
            volumes/
                coronacases_org_001.nii.gz
                ....
            metadata.csv
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

    csv_path = os.path.join(root_path, "metadata.csv")

    with open(csv_path) as fp:
        csv_reader = csv.DictReader(fp)
        for attributes in csv_reader:
            folder = attributes.pop("folder")
            # The 20 images invovled in "volumes" folder currently are invalid to download.
            if folder == "volumes":
                continue
            image_path = os.path.join(root_path, folder, attributes.pop("filename"))
            category = attributes.pop("finding").strip()
            data = Data(image_path)
            data.label.classification = Classification(
                category=category, attributes=_convert_type(attributes)
            )
            segment.append(data)
    return dataset


def _convert_type(attributes: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in attributes.items():
        if value == "":
            attributes[key] = None
        elif key in _INTEGER_GROUP:
            attributes[key] = int(value)
        elif key in _FLOAT_GROUP:
            attributes[key] = float(value)

    return attributes
