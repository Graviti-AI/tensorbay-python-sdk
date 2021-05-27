#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import os

from ...dataset import Data, Dataset
from ...exception import ModuleImportError
from ...label import Classification

DATASET_NAME_17 = "Flower17"
DATASET_NAME_102 = "Flower102"
_SEGMENT_NAMES_17 = {"train": "trn1", "validation": "val1", "test": "tst1"}
_SEGMENT_NAMES_102 = {"train": "trnid", "validation": "valid", "test": "tstid"}


def Flower17(path: str) -> Dataset:
    """Dataloader of the `17 Category Flower`_ dataset.

    .. _17 Category Flower: http://www.robots.ox.ac.uk/~vgg/data/flowers/17/index.html

    The dataset are 3 separate splits.
    The results in the paper are averaged over the 3 splits.
    We just use (trn1, val1, tst1) to split it.

    The file structure should be like::

                <path>
                    jpg/
                        image_0001.jpg
                        ...
                    datasplits.mat

    Arguments:
        path: The root directory of the dataset.

    Raises:
        ModuleImportError: When the module "scipy" can not be found.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    try:
        from scipy.io import loadmat  # pylint: disable=import-outside-toplevel
    except ModuleNotFoundError as error:
        raise ModuleImportError(error.name) from error  # type: ignore[arg-type]

    root_path = os.path.abspath(os.path.expanduser(path))
    segment_info = loadmat(os.path.join(root_path, "datasplits.mat"))

    dataset = Dataset(DATASET_NAME_17)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog_17.json"))
    index_to_category = dataset.catalog.classification.get_index_to_category()
    for key, value in _SEGMENT_NAMES_17.items():
        segment = dataset.create_segment(key)
        segment_info[value][0].sort()
        for index in segment_info[value][0]:
            data = Data(os.path.join(root_path, "jpg", f"image_{index:04d}.jpg"))

            # There are 80 images for each category
            data.label.classification = Classification(
                category=index_to_category[(index - 1) // 80]
            )
            segment.append(data)

    return dataset


def Flower102(path: str) -> Dataset:
    """Dataloader of the `102 Category Flower`_ dataset.

    .. _102 Category Flower: http://www.robots.ox.ac.uk/~vgg/data/flowers/102/index.html

    The file structure should be like::

        <path>
            jpg/
                image_00001.jpg
                ...
            imagelabels.mat
            setid.mat

    Arguments:
        path: The root directory of the dataset.

    Raises:
        ModuleImportError: When the module "scipy" can not be found.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    try:
        from scipy.io import loadmat  # pylint: disable=import-outside-toplevel
    except ModuleNotFoundError as error:
        raise ModuleImportError(error.name) from error  # type: ignore[arg-type]

    root_path = os.path.abspath(os.path.expanduser(path))
    labels = loadmat(os.path.join(root_path, "imagelabels.mat"))["labels"][0]
    segment_info = loadmat(os.path.join(root_path, "setid.mat"))

    dataset = Dataset(DATASET_NAME_102)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog_102.json"))
    index_to_category = dataset.catalog.classification.get_index_to_category()
    for key, value in _SEGMENT_NAMES_102.items():
        segment = dataset.create_segment(key)
        segment_info[value][0].sort()
        for index in segment_info[value][0]:
            data = Data(os.path.join(root_path, "jpg", f"image_{index:05d}.jpg"))
            data.label.classification = Classification(
                index_to_category[int(labels[index - 1]) - 1]
            )
            segment.append(data)
    return dataset
