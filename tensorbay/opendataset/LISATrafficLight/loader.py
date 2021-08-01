#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import csv
import os
import re

from ...dataset import Data, Dataset, Segment
from ...exception import FileStructureError
from ...label import Classification, LabeledBox2D
from ...utility import chunked
from .._utility import glob

DATASET_NAME = "LISATrafficLight"

SUPERCATEGORY_INDEX = {
    "frameAnnotationsBOX.csv": "BOX",
    "frameAnnotationsBULB.csv": "BULB",
}


def LISATrafficLight(path: str) -> Dataset:
    """Dataloader of the `LISA Traffic Light`_ dataset.

    .. _LISA Traffic Light: http://cvrr.ucsd.edu/LISA/datasets.html

    The file structure should be like::

        <path>
            Annotations/Annotations/
                daySequence1/
                daySequence2/
                dayTrain/
                    dayClip1/
                    dayClip10/
                    ...
                    dayClip9/
                nightSequence1/
                nightSequence2/
                nightTrain/
                    nightClip1/
                    nightClip2/
                    ...
                    nightClip5/
            daySequence1/daySequence1/
            daySequence2/daySequence2/
            dayTrain/dayTrain/
                dayClip1/
                dayClip10/
                ...
                dayClip9/
            nightSequence1/nightSequence1/
            nightSequence2/nightSequence2/
            nightTrain/nightTrain/
                nightClip1/
                nightClip2/
                ...
                nightClip5/

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    Raises:
        FileStructureError: When frame number is discontinuous.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    annotation_path = os.path.join(root_path, "Annotations", "Annotations")

    dataset = Dataset(DATASET_NAME)
    dataset.notes.is_continuous = True
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    csv_paths = glob(os.path.join(annotation_path, "**", "*.csv"), recursive=True)

    for box_csv_path, bulb_csv_path in chunked(csv_paths, 2):
        segment = dataset.create_segment(_get_segment_name(box_csv_path))

        prefix = _get_path_prefix(annotation_path, box_csv_path)
        classification = _get_classification(prefix)

        filedir = os.path.join(root_path, prefix)
        image_paths = glob(os.path.join(filedir, "*.jpg"))

        # Check the frame_number from filename: "daySequence1--00345.jpg"
        if _get_frame_number(image_paths[-1]) + 1 != len(image_paths):
            raise FileStructureError(f"Discontinuous frame number in '{filedir}'")

        for image_path in image_paths:
            data = Data(image_path)
            data.label.box2d = []
            if classification:
                data.label.classification = Classification(classification)
            segment.append(data)

        _add_labels(segment, box_csv_path)
        _add_labels(segment, bulb_csv_path)

    return dataset


def _get_frame_number(filename: str) -> int:
    return int(filename[-9:-4])


def _get_path_prefix(annotation_path: str, csv_path: str) -> str:
    relpath = os.path.relpath(csv_path, annotation_path)
    splits = relpath.split(os.sep)[:-1]
    return os.path.join(splits[0], *splits, "frames")


def _get_segment_name(csv_path: str) -> str:
    with open(csv_path, "r", encoding="utf-8") as fp:
        reader = csv.DictReader(fp, delimiter=";")
        first_filename = next(reader)["Filename"]
        header = first_filename[: first_filename.index("-")].replace("/", "-")
        return re.sub(r"\d+", lambda match: f"{int(match.group(0)):02}", header, 1)


def _get_supercategory(csv_path: str) -> str:
    basename = os.path.basename(csv_path)
    return SUPERCATEGORY_INDEX[basename]


def _get_classification(path_prefix: str) -> str:
    if path_prefix.startswith("day"):
        return "day"

    if path_prefix.startswith("night"):
        return "night"

    return ""


def _add_labels(segment: Segment, csv_path: str) -> None:
    supercategory = _get_supercategory(csv_path)

    with open(csv_path, "r", encoding="utf-8") as fp:
        reader = csv.DictReader(fp, delimiter=";")
        for row in reader:
            frame_number = int(row["Origin frame number"])
            data = segment[frame_number]

            label = LabeledBox2D(
                int(row["Upper left corner X"]),
                int(row["Upper left corner Y"]),
                int(row["Lower right corner X"]),
                int(row["Lower right corner Y"]),
                category=".".join([supercategory, row["Annotation tag"]]),
            )
            data.label.box2d.append(label)
