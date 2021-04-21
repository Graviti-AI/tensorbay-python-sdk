#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import csv
import os

from ...dataset import Data, Dataset
from ...label import Classification
from .._utility import glob

DATASET_NAME_ABSTRACT = "ImageEmotionAbstract"
DATASET_NAME_ARTPHOTO = "ImageEmotionArtPhoto"


def ImageEmotionAbstract(path: str) -> Dataset:
    """Dataloader of the `Image Emotion-abstract`_ dataset.

    .. _Image Emotion-abstract: https://www.imageemotion.org/

    The file structure should be like::

        <path>
            ABSTRACT_groundTruth.csv
            abstract_xxxx.jpg
            ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = Dataset(DATASET_NAME_ABSTRACT)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog_abstract.json"))
    segment = dataset.create_segment()

    csv_path = os.path.join(root_path, "ABSTRACT_groundTruth.csv")
    with open(csv_path, "r", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        reader.fieldnames = [
            field.strip("'") for field in reader.fieldnames  # type:ignore[union-attr]
        ]

        for row in reader:
            image_path = os.path.join(root_path, row.pop("").strip("'"))

            data = Data(image_path)
            values = {key: int(value) for key, value in row.items()}

            data.label.classification = Classification(attributes=values)
            segment.append(data)

    return dataset


def ImageEmotionArtphoto(path: str) -> Dataset:
    """Dataloader of the `Image Emotion-art Photo`_ dataset.

    .. _Image Emotion-art Photo: https://www.imageemotion.org/

    The file structure should be like::

        <path>
            <filename>.jpg
            ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = Dataset(DATASET_NAME_ARTPHOTO)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog_artphoto.json"))
    segment = dataset.create_segment()

    image_paths = glob(os.path.join(root_path, "*.jpg"))

    for image_path in image_paths:
        image_category = os.path.basename(image_path).split("_", 1)[0]

        data = Data(image_path)
        data.label.classification = Classification(category=image_category)
        segment.append(data)

    return dataset
