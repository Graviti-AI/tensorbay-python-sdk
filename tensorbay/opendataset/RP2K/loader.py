#!/usr/bin/env python3
#
# Copytright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of RP2K dataset."""

import os
from glob import glob
from typing import Iterable, List

from tensorbay.dataset import Data, Dataset
from tensorbay.label import Classification

DATASET_NAME = "RP2K"


def RP2K(path: str) -> Dataset:
    """`RP2K <https://www.pinlandata.com/rp2k_dataset>`_ dataset.

    The file structure of RP2K looks like::

        <path>
            all/
                test/
                    <catagory>/
                        <image_name>.jpg
                        ...
                    ...
                train/
                    <catagory>/
                        <image_name>.jpg
                        ...
                    ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.join(os.path.abspath(os.path.expanduser(path)), "all")
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name in ("train", "test"):
        segment = dataset.create_segment(segment_name)
        segment_path = os.path.join(root_path, segment_name)
        categories = os.listdir(segment_path)
        categories.sort()
        for category in categories:
            category_dir = os.path.join(segment_path, category)
            if not os.path.isdir(category_dir):
                continue
            image_paths = _glob(category_dir, ("*.jpg", "*.png"))
            for image_path in image_paths:
                remote_path = os.path.basename(image_path).replace(" ", "_")
                data = Data(local_path=image_path, target_remote_path=remote_path)
                data.label.classification = Classification(category)
                segment.append(data)

    return dataset


def _glob(category_dir: str, patterns: Iterable[str]) -> List[str]:
    file_paths = []

    for pattern in patterns:
        file_paths.extend(glob(os.path.join(category_dir, pattern)))

    file_paths.sort()
    return file_paths
