#!/usr/bin/env python3
#
# Copytright 2020 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name, missing-module-docstring

import csv
import os
from collections import defaultdict
from typing import Dict, List

from ...dataset import Data, Dataset
from ...label import Box2DSubcatalog, Classification, ClassificationSubcatalog, LabeledBox2D
from .._utility import glob

_DATASET_NAME = "UAVDT"

_MODES = ("train", "test")

_FIELDNAMES = (
    "frame_index",
    "target_id",
    "bbox_left",
    "bbox_top",
    "bbox_width",
    "bbox_height",
    "out_of_view",
    "occlusion",
    "object_category",
)

_XYWH_KEYS = _FIELDNAMES[2:6]


def UAVDT(path: str) -> Dataset:
    """Dataloader of the `UAVDT`_ Dataset.

    .. _UAVDT: https://sites.google.com/site/daviddo0323/projects/uavdt

    The "score", "in-view", "occlusion" fields in MOT Groundtruth file(``*_gt.txt``) are constant,
    and other fields in that file are the same with such fields in DET Groundtruth file
    (``*_gt_whole.txt``). Therefore, they are not included in the dataloader.

    The Ignore Areas file(``*_gt_ignore.txt``) is useless,
    so they are not included in the dataloader neither.

    The file structure of UAVDT looks like::

        <path>
            M_attr/
                test/
                    M0203_attr.txt
                    ...
                train/
                    M0101_attr.txt
                    ...
            UAVDT_Benchmark_M/
                M0101/
                    img000001.jpg
                    ...
                ...
            UAV-benchmark-MOTD_v1.0/
                GT/
                    M0101_gt_ignore.txt
                    M0101_gt.txt
                    M0101_gt_whole.txt
                    ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = Dataset(_DATASET_NAME)
    dataset.notes.is_continuous = True
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for mode in _MODES:
        for sequence_attributes_path in glob(os.path.join(root_path, "M_attr", mode, "*.txt")):
            sequence = os.path.basename(sequence_attributes_path)[:5]
            segment = dataset.create_segment(f"{mode}-{sequence}")

            classification = _extract_classification(
                sequence_attributes_path, dataset.catalog.classification
            )

            frame_id_box2d_map = _extract_box2d(root_path, sequence, dataset.catalog.box2d)

            image_paths = glob(os.path.join(root_path, "UAV-benchmark-M", sequence, "*.jpg"))
            for image_path in image_paths:
                data = Data(image_path)
                data.label.classification = classification
                # The image_name looks like `img<frame_id>.jpg`.
                # The frame_id is consist of six digital numbers.
                data.label.box2d = frame_id_box2d_map[int(os.path.basename(image_path)[3:9])]
                segment.append(data)

    return dataset


def _extract_classification(
    path: str, classification_catalog: ClassificationSubcatalog
) -> Classification:
    with open(path) as fp:
        attribute_names = classification_catalog.attributes.keys()
        csv_reader = csv.reader(fp)
        elements = next(csv_reader)
        attributes = {
            attribute_name: bool(int(value))
            for attribute_name, value in zip(attribute_names, elements)
        }

    return Classification(attributes=attributes)


def _extract_box2d(
    path: str, sequence: str, box2d_catalog: Box2DSubcatalog
) -> Dict[int, List[LabeledBox2D]]:
    attributes = box2d_catalog.attributes
    category_names = box2d_catalog.categories.keys()

    out_of_view_level = attributes["out_of_view"].enum
    occlusion_level = attributes["occlusion"].enum

    ground_truth_path = os.path.join(path, "UAV-benchmark-MOTD_v1.0", "GT")
    frame_id_ground_truth_map = defaultdict(list)
    with open(os.path.join(ground_truth_path, f"{sequence}_gt_whole.txt")) as fp:
        for elements in csv.DictReader(fp, fieldnames=_FIELDNAMES):
            box2d = LabeledBox2D.from_xywh(
                *(int(elements[key]) for key in _XYWH_KEYS),
                category=category_names[int(elements["object_category"]) - 1],
                attributes={
                    "out_of_view": out_of_view_level[int(elements["out_of_view"]) - 1],
                    "occlusion": occlusion_level[int(elements["occlusion"]) - 1],
                },
                instance=elements["target_id"],
            )
            frame_id = int(elements["frame_index"])
            frame_id_ground_truth_map[frame_id].append(box2d)

    return frame_id_ground_truth_map
