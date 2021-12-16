#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of COCO2017 dataset."""

import json
import os
from collections import defaultdict
from typing import Any, DefaultDict, Dict, List, Tuple

import numpy as np

from tensorbay.dataset import Data, Dataset
from tensorbay.label import (
    Label,
    LabeledBox2D,
    LabeledKeypoints2D,
    LabeledMultiPolygon,
    LabeledRLE,
    PanopticMask,
)
from tensorbay.opendataset._utility.glob import glob
from tensorbay.utility.itertools import chunked

try:
    from PIL import Image
except ModuleNotFoundError:
    from tensorbay.opendataset._utility.mocker import Image  # pylint:disable=ungrouped-imports

DATASET_NAME = "COCO2017"
_LABELED_SEGMENT_NAMES = ("train", "val")
_UNLABELED_SEGMENT_NAMES = ("test", "unlabeled")


def COCO2017(path: str) -> Dataset:
    """`COCO2017 <https://cocodataset.org/#home>`_ dataset.

    The file structure should be like::

        <path>
            annotations/
                panoptic_train2017/
                    000000116037.png
                    000000116040.png
                    ...
                panoptic_val2017/
                instances_train2017.json
                instances_val2017.json
                panoptic_train2017.json
                panoptic_val2017.json
                person_keypoints_train2017.json
                person_keypoints_val2017.json
            train2017/
                000000116026.jpg
                000000116031.jpg
                ...
            test2017/
            val2017/
            unlabeled2017/

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class: `~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name in _LABELED_SEGMENT_NAMES:
        segment = dataset.create_segment(segment_name)
        annotation_path = os.path.join(root_path, "annotations")
        task_information = _get_information(annotation_path, segment_name)
        categories = task_information["categories"]
        for image_path in glob(os.path.join(root_path, f"{segment_name}2017", "*.jpg")):
            data = Data(image_path)
            image_stem = os.path.splitext(os.path.basename(image_path))[0]
            image_id = int(image_stem)

            label = _get_instance_label(
                task_information["instances_annotations"], image_id, categories
            )
            label.keypoints2d = _get_keypoints2d(
                task_information["person_keypoints_annotations"], image_id, categories
            )
            label.box2d.extend(
                _get_panoptic_box2d(task_information["panoptic_annotations"], image_id, categories)
            )
            label.panoptic_mask = _get_panoptic_mask(
                annotation_path,
                segment_name,
                image_stem,
                task_information["panoptic_annotations"],
                image_id,
            )
            data.label = label
            segment.append(data)

    for segment_name in _UNLABELED_SEGMENT_NAMES:
        segment = dataset.create_segment(segment_name)
        for image_path in glob(os.path.join(root_path, f"{segment_name}2017", "*.jpg")):
            segment.append(Data(image_path))

    return dataset


def _get_information(annotation_path: str, segment_name: str) -> Dict[str, Any]:
    task_information: Dict[str, Any] = {}
    for task in ("instances", "person_keypoints", "panoptic"):
        with open(
            os.path.join(annotation_path, f"{task}_{segment_name}2017.json"), encoding="utf-8"
        ) as fp:
            file_json = json.load(fp)

        task_annotation: DefaultDict[int, Any] = defaultdict(list)
        for annotation in file_json["annotations"]:
            task_annotation[annotation["image_id"]].append(annotation)
        task_information[f"{task}_annotations"] = task_annotation

        if task == "panoptic":
            task_information["categories"] = {
                category["id"]: f"{category['supercategory']}.{category['name']}"
                for category in file_json["categories"]
            }
    return task_information


def _get_instance_label(
    instances_annotations: Dict[int, Any], image_id: int, categories: Dict[int, str]
) -> Label:
    label: Label = Label()
    label.box2d = []
    label.multi_polygon = []
    label.rle = []
    if image_id not in instances_annotations:
        return label

    for annotation in instances_annotations[image_id]:
        category = categories[annotation["category_id"]]
        label.box2d.append(LabeledBox2D.from_xywh(*annotation["bbox"], category=category))
        if annotation["iscrowd"] == 0:
            points = [chunked(coordinates, 2) for coordinates in annotation["segmentation"]]
            label.multi_polygon.append(LabeledMultiPolygon(points, category=category))
        else:
            label.rle.append(LabeledRLE(annotation["segmentation"]["counts"], category=category))
    return label


def _get_keypoints2d(
    person_keypoints_annotations: Dict[int, Any], image_id: int, categories: Dict[int, str]
) -> List[LabeledKeypoints2D]:
    if image_id not in person_keypoints_annotations:
        return []

    keypoints2d: List[LabeledKeypoints2D] = []
    for annotation in person_keypoints_annotations[image_id]:
        points = chunked(annotation["keypoints"], 3)
        category = categories[annotation["category_id"]]
        keypoints2d.append(LabeledKeypoints2D(points, category=category))

    return keypoints2d


def _get_panoptic_box2d(
    panoptic_annotations: Dict[int, Any], image_id: int, categories: Dict[int, str]
) -> List[LabeledBox2D]:
    if image_id not in panoptic_annotations:
        return []

    box2d: List[LabeledBox2D] = []
    for annotation in panoptic_annotations[image_id]:
        for segment_info in annotation["segments_info"]:
            # category_id 1-91 are thing categories from the detection task
            # category_id 92-200 are stuff categories from the stuff task
            if segment_info["category_id"] > 91:
                category = categories[segment_info["category_id"]]
                box2d.append(LabeledBox2D.from_xywh(*segment_info["bbox"], category=category))
    return box2d


def _get_panoptic_mask(
    annotation_path: str,
    segment_name: str,
    image_stem: str,
    panoptic_annotations: Dict[int, Any],
    image_id: int,
) -> PanopticMask:
    compress_pixel, new_mask_path = _save_mask(annotation_path, segment_name, image_stem)

    category_ids = {}
    annotation = panoptic_annotations[image_id][0]
    for info in annotation["segments_info"]:
        category_ids[compress_pixel[info["id"]]] = info["category_id"]
    panoptic_mask = PanopticMask(local_path=new_mask_path)
    panoptic_mask.all_category_ids = category_ids
    return panoptic_mask


def _save_mask(
    annotation_path: str, segment_name: str, image_stem: str
) -> Tuple[Dict[int, int], str]:
    new_file_path = os.path.join(annotation_path, f"new_panoptic_{segment_name}2017")
    os.makedirs(new_file_path, exist_ok=True)
    mask_name = f"{image_stem}.png"

    array = np.array(
        Image.open(os.path.join(annotation_path, f"panoptic_{segment_name}2017", mask_name)),
        dtype=int,
    )
    mask_array = array[:, :, 0] + array[:, :, 1] * 256 + array[:, :, 2] * 256 * 256

    array_elements = np.unique(mask_array)
    array_elements = np.delete(array_elements, np.where(array_elements == 0))
    map_of_pixel = dict(zip(array_elements, range(1, len(array_elements) + 1)))
    map_of_pixel[0] = 0
    mask_array = np.vectorize(map_of_pixel.get)(mask_array)

    new_mask_path = os.path.join(new_file_path, mask_name)
    Image.fromarray(np.uint8(mask_array)).save(new_mask_path)
    return map_of_pixel, new_mask_path
