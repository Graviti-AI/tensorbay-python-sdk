#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import os

from ...dataset import Data, Dataset
from ...label import Classification
from .._utility import glob

DATASET_NAME = "KylbergTexture"


def KylbergTexture(path: str) -> Dataset:
    """Dataloader of the `Kylberg Texture`_ dataset.

    .. _Kylberg Texture: http://www.cb.uu.se/~gustaf/texture/

    The file structure should be like::

        <path>
            originalPNG/
                <imagename>.png
                ...
            withoutRotateAll/
                <imagename>.png
                ...
            RotateAll/
                <imagename>.png
                ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name, label_getter in _LABEL_GETTERS.items():
        image_paths = glob(os.path.join(root_path, segment_name, "*.png"))

        segment = dataset.create_segment(segment_name)

        for image_path in image_paths:
            data = Data(image_path)
            stem = os.path.splitext(os.path.basename(image_path))[0]
            data.label.classification = label_getter(stem)
            segment.append(data)

    return dataset


def _get_original_png_label(stem: str) -> Classification:
    """Get label from stem of originalPng image name.

    Arguments:
        stem: Stem of originalPng image name like "blanket1-a".

    Returns:
        Label of originalPng image.

    """
    class_name, original_image_number = stem.split("-", 1)
    attributes = {
        "original image sample number": original_image_number,
        "patch number": None,
        "rotated degrees": 0,
    }
    return Classification(category=class_name, attributes=attributes)


def _get_without_rotate_all_label(stem: str) -> Classification:
    """Get label from stem of withoutRotateAll image name.

    Arguments:
        stem: Stem of withoutRotateAll image name like "blanket1-a-p001".

    Returns:
        Label of withoutRotateAll image.

    """
    class_name, original_image_number, patch_number = stem.split("-", 2)
    attributes = {
        "original image sample number": original_image_number,
        "patch number": int(patch_number[1:]),
        "rotated degrees": 0,
    }
    return Classification(category=class_name, attributes=attributes)


def _get_rotated_all_label(stem: str) -> Classification:
    """Get label from stem of RotateAll image name.

    Arguments:
        stem: Stem of RotateAll image name like "blanket1-a-p001-r30".

    Returns:
        Label of RotateAll image.

    """
    class_name, original_image_number, patch_number, rotated_degrees = stem.split("-", 3)
    attributes = {
        "original image sample number": original_image_number,
        "patch number": int(patch_number[1:]),
        "rotated degrees": int(rotated_degrees[1:]),
    }
    return Classification(category=class_name, attributes=attributes)


_LABEL_GETTERS = {
    "originalPNG": _get_original_png_label,
    "withoutRotateAll": _get_without_rotate_all_label,
    "RotatedAll": _get_rotated_all_label,
}
