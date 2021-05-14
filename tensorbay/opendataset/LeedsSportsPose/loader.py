#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import os

from ...dataset import Data, Dataset
from ...exception import ModuleImportError
from ...geometry import Keypoint2D
from ...label import LabeledKeypoints2D
from .._utility import glob

DATASET_NAME = "LeedsSportsPose"


def LeedsSportsPose(path: str) -> Dataset:
    """Dataloader of the `Leeds Sports Pose`_ dataset.

    .. _Leeds Sports Pose: https://sam.johnson.io/research/lsp.html

    The folder structure should be like::

        <path>
            joints.mat
            images/
                im0001.jpg
                im0002.jpg
                ...

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

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    segment = dataset.create_segment()

    mat = loadmat(os.path.join(root_path, "joints.mat"))

    joints = mat["joints"].T
    image_paths = glob(os.path.join(root_path, "images", "*.jpg"))
    for image_path in image_paths:
        data = Data(image_path)
        data.label.keypoints2d = []
        index = int(os.path.basename(image_path)[2:6]) - 1  # get image index from "im0001.jpg"

        keypoints = LabeledKeypoints2D()
        for keypoint in joints[index]:
            keypoints.append(  # pylint: disable=no-member  # pylint issue #3131
                Keypoint2D(keypoint[0], keypoint[1], int(not keypoint[2]))
            )

        data.label.keypoints2d.append(keypoints)
        segment.append(data)
    return dataset
