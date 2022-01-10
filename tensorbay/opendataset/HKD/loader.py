#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT Licence.
#
# pylint: disable=invalid-name

"""Dataloader for Finger Tapping Hand Keypoints Dataset(HKD)."""

import csv
import os

from tensorbay.dataset import Data, Dataset
from tensorbay.label import LabeledKeypoints2D
from tensorbay.utility import chunked

DATASET_NAME = "HKD"
_SEGMENT_INFO = {
    "subject1": (
        "subject1_fingercount_2D_Annotations_cropped.csv",
        "subject1_fingercount_cropframe_{}.jpg",
    ),
    "subject2": (
        "subject2_fingercount_2D_Annotations_cropped.csv",
        "subject2_fingercount_cropframe_{}.jpg",
    ),
    "subject3": (
        "fingerappose_subject3_2D_Annotations_cropped.csv",
        "fingerappose_subject3_cropframe_{}.jpg",
    ),
    "subject4": ("subject4_2D_Annotations_cropped.csv", "subject4_cropframe_{}.jpg"),
}


def HKD(path: str) -> Dataset:
    """`HKD <http://vlm1.uta.edu/~srujana/HandPoseDataset/HK_Dataset.html>`_ dataset.

    The file structure should be like::

        <path>
            AnnotatedData_subject1/
                CropImages/
                    subject1_fingercount_cropframe_2.jpg
                    subject1_fingercount_cropframe_3.jpg
                    ...
                    subject1_fingercount_cropframe_210.jpg
                subject1_fingercount_2D_Annotations_cropped.csv

            AnnotatedData_subject2/
                CropImages/
                    subject2_fingercount_cropframe_2.jpg
                    subject2_fingercount_cropframe_3.jpg
                    ...
                    subject2_fingercount_cropframe_207.jpg
                subject2_fingercount_2D_Annotations_cropped.csv

            AnnotatedData_subject3/
                CropImages/
                    fingerappose_subject3_cropframe_2.jpg
                    fingerappose_subject3_cropframe_3.jpg
                    ...
                    fingerappose_subject3_cropframe_235.jpg
                fingerappose_subject3_2D_Annotations_cropped.csv

            AnnotatedData_subject4/
                CropImages/
                    subject4_cropframe_2.jpg
                    subject4_cropframe_3.jpg
                    ...
                    subject4_cropframe_147.jpg
                subject4_2D_Annotations_cropped.csv

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    for segment_name, (csv_name, image_name_template) in _SEGMENT_INFO.items():
        segment = dataset.create_segment(segment_name)
        segment_path = os.path.join(root_path, f"AnnotatedData_{segment_name}")
        csv_path = os.path.join(root_path, segment_path, csv_name)
        with open(csv_path, encoding="utf-8") as fp:
            # The csv files should be like::
            #     subject1_fingercount_2D_Annotations_cropped.csv
            #         2,4.523,28.569,136.8,181.37,154.63,80.348,130.86,57.322,...
            #         3,4.523,32.731,135.31,176.17,147.2,80.348,123.43,65.493,...
            #         4,-2.413,39.668,149.41,164.28,143.47,70.692,137.53,64.75,...
            #         5,-1.026,31.344,138.77,178.4,136.54,78.863,135.06,75.149,...
            #         ...
            #     ...
            for csv_line in csv.reader(fp):
                image_path = os.path.join(
                    segment_path, "CropImages", image_name_template.format(csv_line.pop(0))
                )
                data = Data(image_path)
                data.label.keypoints2d = [LabeledKeypoints2D(chunked(map(float, csv_line), 2))]
                segment.append(data)
    return dataset
