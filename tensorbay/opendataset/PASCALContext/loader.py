#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of PASCALContext dataset."""

import os

from tensorbay.dataset import Data, Dataset
from tensorbay.exception import ModuleImportError
from tensorbay.label import SemanticMask
from tensorbay.opendataset._utility import glob

DATASET_NAME = "PASCALContext"


def PASCALContext(mask_path: str, image_path: str) -> Dataset:
    """`PASCALContext <https://cs.stanford.edu/~roozbeh/pascal-context/>`_ dataset.

    The file structure should be like::

        <mask_path>
            <image_name>.png
            ...

        <image_path>
            <image_name>.jpg
            ...

    Arguments:
        mask_path: The root directory of the dataset mask.
        image_path: The root directory of the dataset image.

    Returns:
        Loaded :class: `~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_mask_path = os.path.abspath(os.path.expanduser(mask_path))
    root_image_path = os.path.abspath(os.path.expanduser(image_path))

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    segment = dataset.create_segment("trainval")
    for mask_filename in glob(os.path.join(root_mask_path, "*.png")):
        stem = os.path.splitext(os.path.basename(mask_filename))[0]
        data = Data(os.path.join(root_image_path, f"{stem}.jpg"))
        data.label.semantic_mask = SemanticMask(mask_filename)
        segment.append(data)

    return dataset


def convert_mask(path: str, mask_path: str) -> None:
    """Convert the mat format labels of the PASCALContext dataset to masks.

    The file structure of the input path should be like::

            <path>
                <trainval>
                    <image_name>.mat
                    ...

    Arguments:
        path: The root directory of the dataset.
        mask_path: The root directory where to save the masks.

    Raises:
        ModuleImportError: When the module "scipy" or "Pillow" can not be found.

    """
    try:
        from PIL import Image  # pylint: disable=import-outside-toplevel
        from scipy.io import loadmat  # pylint: disable=import-outside-toplevel
    except ModuleNotFoundError as error:
        module_name = error.name
        package_name = "Pillow" if module_name == "PIL" else None
        raise ModuleImportError(module_name=module_name, package_name=package_name) from error

    root_path = os.path.abspath(os.path.expanduser(path))
    root_mask_path = os.path.abspath(os.path.expanduser(mask_path))

    for mat_path in glob(os.path.join(root_path, "trainval", "*.mat")):
        stem = os.path.splitext(os.path.basename(mat_path))[0]
        mat = loadmat(mat_path)
        image = Image.fromarray(mat["LabelMap"])
        image.save(os.path.join(root_mask_path, f"{stem}.png"))
