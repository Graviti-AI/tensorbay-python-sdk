#!/usr/bin/env python3
#
# Copytright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import os
from itertools import islice
from typing import List

from ...dataset import Data, Dataset
from ...geometry import Keypoint2D
from ...label import LabeledKeypoints2D
from .._utility import glob

DATASET_NAME = "BioIDFace"


def BioIDFace(path: str) -> Dataset:
    """Dataloader of `The BioID Face`_ Dataset.

    .. _The BioID Face: https://www.bioid.com/facedb/

    The folder structure should be like::

                <path>
                    BioID-FaceDatabase-V1.2/
                        BioID_0000.eye
                        BioID_0000.pgm
                        ...
                    points_20/
                        bioid_0000.pts

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    segment = dataset.create_segment()

    image_paths = glob(os.path.join(root_path, "BioID-FaceDatabase-V1.2", "*.pgm"))
    face_keypoints_paths = glob(os.path.join(root_path, "points_20", "*.pts"))

    for image_path, face_keypoints_path in zip(image_paths, face_keypoints_paths):
        data = Data(image_path)
        data.label.keypoints2d = _get_label(
            f"{os.path.splitext(image_path)[0]}.eye", face_keypoints_path
        )

        segment.append(data)

    return dataset


def _get_label(eye_keypoints_path: str, face_keypoints_path: str) -> List[LabeledKeypoints2D]:
    eye_keypoints = LabeledKeypoints2D(category="EyePosition")
    with open(eye_keypoints_path, "r", encoding="utf-8") as fp:
        fp.readline()  # The first line is like: #LX     LY      RX      RY
        lx, ly, rx, ry = map(int, fp.readline().split())
        eye_keypoints.append(Keypoint2D(lx, ly))  # pylint: disable=no-member
        eye_keypoints.append(Keypoint2D(rx, ry))  # pylint: disable=no-member

    face_keypoints = LabeledKeypoints2D(category="Face")
    with open(face_keypoints_path, "r", encoding="utf-8") as fp:
        # The annotation file is like:
        #  1 version: 1
        #  2 n_points: 20
        #  3 {
        #  4 159.128 108.541
        #    ...
        # 24 }
        for line in islice(fp, 3, 23):
            x, y = map(float, line.split())
            face_keypoints.append(Keypoint2D(x, y))  # pylint: disable=no-member

    return [eye_keypoints, face_keypoints]
