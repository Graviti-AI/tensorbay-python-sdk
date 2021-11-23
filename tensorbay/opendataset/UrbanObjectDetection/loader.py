#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name, missing-module-docstring

"""Dataloader of UrbanObjectDetection dataset."""

import os

from tensorbay.dataset import Dataset
from tensorbay.opendataset._utility import get_boolean_attributes, get_voc_detection_data

DATASET_NAME = "UrbanObjectDetection"
_SEGMENT_NAMES = ("train", "val", "test")


def UrbanObjectDetection(path: str) -> Dataset:
    """`UrbanObjectDetection <http://www.rovit.ua.es/dataset/traffic/>`_ dataset.

    The file structure should be like::

        <path>
            Annotations/
                <image_name>.xml
                ...
            JPEGImages/
                <image_name>.jpg
                ...
            ImageSets/
                train.txt
                val.txt
                test.txt

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    annotation_path = os.path.join(root_path, "Annotations")
    image_path = os.path.join(root_path, "JPEGImages")
    image_set_path = os.path.join(root_path, "ImageSets")

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    boolean_attributes = get_boolean_attributes(dataset.catalog.box2d)

    for segment_name in _SEGMENT_NAMES:
        segment = dataset.create_segment(segment_name)
        with open(os.path.join(image_set_path, f"{segment_name}.txt"), encoding="utf-8") as fp:
            for stem in fp:
                segment.append(
                    get_voc_detection_data(
                        stem.rstrip(), image_path, annotation_path, boolean_attributes
                    )
                )
    return dataset
