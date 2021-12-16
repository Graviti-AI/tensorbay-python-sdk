#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloaders of DAVIS2017SemiSupervised dataset and DAVIS2017Unsupervised dataset."""

import os
from itertools import product
from typing import Callable, Dict, Iterator

from tensorbay.dataset import Data, Dataset
from tensorbay.label import InstanceMask, SemanticMask
from tensorbay.opendataset._utility import glob

_RESOLUTIONS = ("480p", "Full-Resolution")
_SEMI_SUPERVISED_DATASET_NAME = "DAVIS2017SemiSupervised"
_UNSUPERVISED_DATASET_NAME = "DAVIS2017Unsupervised"


def DAVIS2017SemiSupervised(path: str) -> Dataset:
    """`DAVIS2017SemiSupervised <https://davischallenge.org/davis2017/code.html>`_ dataset.

    The file structure should be like::

        <path>
            Annotations/
                480p/
                    aerobatics/
                        00000.png
                    bear/
                    ...
                Full-Resolution/
                    aerobatics/
                        00000.png
                    bear/
                    ...
            Annotations_semantics/
                480p/
                    aerobatics/
                        00000.png
                    bear/
                    ...
                Full-Resolution/
                    aerobatics/
                        00000.png
                    bear/
                    ...
            JPEGImages/
                480p/
                    aerobatics/
                        00000.jpg
                        00001.jpg
                        ...
                    bear/
                    ...
                Full-Resolution/
                    aerobatics/
                        00000.jpg
                        00001.jpg
                        ...
                    bear/
                    ...
            ImageSets/
                2017/
                    test-challenge.txt
                    test-dev.txt
                    train.txt
                    val.txt

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class: `~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset(_SEMI_SUPERVISED_DATASET_NAME)
    dataset.notes.is_continuous = True
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog_semi_supervised.json"))

    data_getters: Dict[str, Callable[..., Data]] = {
        "train.txt": _get_semi_supervised_labeled_data,
        "val.txt": _get_semi_supervised_labeled_data,
        "test-dev.txt": lambda image_path, *args: Data(image_path),
        "test-challenge.txt": lambda image_path, *args: Data(image_path),
    }

    for file_path, data_getter in data_getters.items():
        for resolution, segment_name in product(
            _RESOLUTIONS,
            _generate_segment_name(os.path.join(root_path, "ImageSets", "2017", file_path)),
        ):
            stem = os.path.splitext(file_path)[0]
            segment = dataset.create_segment(f"{stem}_{segment_name}_{resolution}")
            image_paths = glob(
                os.path.join(root_path, "JPEGImages", resolution, segment_name, "*.jpg")
            )
            first_image_path = image_paths.pop(0)
            #  In the test segment of the semi_supervised task, only the mask of the first image
            #  will be given.
            segment.append(
                _get_semi_supervised_labeled_data(
                    first_image_path, root_path, resolution, segment_name
                )
            )
            for image_path in image_paths:
                segment.append(data_getter(image_path, root_path, resolution, segment_name))
    return dataset


def DAVIS2017Unsupervised(path: str) -> Dataset:
    """`DAVIS2017Unsupervised <https://davischallenge.org/davis2017/code.html>`_ dataset.

    The file structure should be like::

        <path>
            Annotations_unsuperviseds/
                480p/
                    bear/
                        00000.png
                        00001.png
                        ...
                    ...
                Full-Resolution/
                    bear/
                        00000.png
                        00001.png
                        ...
                    ...
            JPEGImages/
                480p/
                    aerobatics/
                        00000.jpg
                        00001.jpg
                        ...
                    bear/
                        00000.jpg
                        00001.jpg
                        ...
                    ...
                Full-Resolution/
                    aerobatics/
                        00000.jpg
                        00001.jpg
                        ...
                    bear/
                        00000.jpg
                        00001.jpg
                        ...
                    ...
            ImageSets/
                2017/
                    train.txt
                    val.txt
                2019/
                    test-challenge.txt
                    test-dev.txt

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class: `~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset(_UNSUPERVISED_DATASET_NAME)
    dataset.notes.is_continuous = True
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog_unsupervised.json"))

    data_getters: Dict[str, Callable[..., Data]] = {
        os.path.join("2017", "train.txt"): _get_unsupervised_labeled_data,
        os.path.join("2017", "val.txt"): _get_unsupervised_labeled_data,
        os.path.join("2019", "test-dev.txt"): lambda image_path, *args: Data(image_path),
        os.path.join("2019", "test-challenge.txt"): lambda image_path, *args: Data(image_path),
    }

    for file_path, data_getter in data_getters.items():
        for resolution, segment_name in product(
            _RESOLUTIONS,
            _generate_segment_name(os.path.join(root_path, "ImageSets", file_path)),
        ):
            stem = os.path.splitext(os.path.basename(file_path))[0]
            segment = dataset.create_segment(f"{stem}_{segment_name}_{resolution}")
            for image_path in glob(
                os.path.join(root_path, "JPEGImages", resolution, segment_name, "*.jpg")
            ):
                segment.append(data_getter(image_path, root_path, resolution, segment_name))
    return dataset


def _generate_segment_name(file_path: str) -> Iterator[str]:
    with open(file_path, encoding="utf-8") as fp:
        for segment_name in fp:
            yield segment_name.strip()


def _get_semi_supervised_labeled_data(
    image_path: str, root_path: str, resolution: str, segment_name: str
) -> Data:
    data = Data(image_path)
    label = data.label
    mask_stem = os.path.splitext(os.path.basename(data.path))[0]
    mask_path = os.path.join(resolution, segment_name, f"{mask_stem}.png")

    label.instance_mask = InstanceMask(os.path.join(root_path, "Annotations", mask_path))
    label.semantic_mask = SemanticMask(os.path.join(root_path, "Annotations_semantics", mask_path))
    return data


def _get_unsupervised_labeled_data(
    image_path: str, root_path: str, resolution: str, segment_name: str
) -> Data:
    data = Data(image_path)
    label = data.label
    mask_stem = os.path.splitext(os.path.basename(data.path))[0]
    mask_path = os.path.join(resolution, segment_name, f"{mask_stem}.png")

    label.instance_mask = InstanceMask(
        os.path.join(root_path, "Annotations_unsupervised", mask_path)
    )
    return data
