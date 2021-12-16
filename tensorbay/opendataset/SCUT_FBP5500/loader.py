#!/usr/bin/env python3
#
# Copytright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of SCUT_FBP5500 dataset."""

import csv
import os
import struct
from itertools import islice

from tensorbay.dataset import Data, Dataset
from tensorbay.geometry.keypoint import Keypoint2D
from tensorbay.label import LabeledKeypoints2D
from tensorbay.utility import chunked

_DATASET_NAME = "SCUT_FBP5500"
_SEGMENT_NAMES = ("train", "test")
_CATEGORY_NAMES = {
    "AF": "Asian females",
    "AM": "Asian males",
    "CF": "Caucasian females",
    "CM": "Caucasian males",
}


def SCUT_FBP5500(path: str) -> Dataset:
    """`SCUT_FBP5500 <https://github.com/HCIILAB/SCUT-FBP5500-Database-Release>`_ dataset.

     The folder structure should be like::

        <path>
            facial landmark/
                <file_name>.pts
                ...
            Images/
                <file_name>.jpg
                ...
            train_test_files/
                split_of_60%training and 40%testing/
                    test.txt
                    train.txt
                ...
            ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))

    segment_path = os.path.join(
        root_path, "train_test_files", "split_of_60%training and 40%testing"
    )
    image_path = os.path.join(root_path, "Images")
    label_path = os.path.join(root_path, "facial landmark")

    dataset = Dataset(_DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name in _SEGMENT_NAMES:
        segment = dataset.create_segment(segment_name)
        with open(os.path.join(segment_path, f"{segment_name}.txt"), encoding="utf-8") as fp:
            reader = csv.reader(fp, delimiter=" ")
            for filename, beauty_score in reader:
                if filename == "CM152.jpg":  # This image lacks 2D keypoints.
                    continue
                segment.append(_get_data(filename, beauty_score, image_path, label_path))
    return dataset


def _get_data(filename: str, beauty_score: str, image_path: str, label_path: str) -> Data:
    stem = os.path.splitext(os.path.basename(filename))[0]
    data = Data(os.path.join(image_path, filename))
    keypoints2d = LabeledKeypoints2D()
    keypoints2d.attributes = {"beauty_score": float(beauty_score)}
    keypoints2d.category = _CATEGORY_NAMES[stem[:2]]
    with open(os.path.join(label_path, f"{stem}.pts"), "rb") as fp:
        points = struct.unpack("i172f", fp.read())
    for x, y in chunked(islice(points, 1, None), 2):
        keypoints2d.append(Keypoint2D(float(x), float(y)))
    data.label.keypoints2d = [keypoints2d]
    return data
