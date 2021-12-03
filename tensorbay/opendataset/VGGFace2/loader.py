#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloaders of VGGFace2 dataset."""

import csv
import os
from collections import defaultdict
from itertools import islice
from typing import DefaultDict, Dict, Tuple

from tensorbay.dataset import Data, Dataset
from tensorbay.label import Classification, LabeledBox2D, LabeledKeypoints2D
from tensorbay.label.basic import AttributeType
from tensorbay.opendataset._utility import glob
from tensorbay.utility import chunked

DATASET_NAME = "VGGFace2"
_SEGMENT_NAMES = ("train", "test")


def VGGFace2(path: str) -> Dataset:
    """`Visual Geometry Group Face 2 <http://www.robots.ox.ac.uk/~vgg/data/vgg_face/>`_ dataset.

    The file structure should be like::

        <path>
            test_list.txt
            train_list.txt
            label/
                identity_meta.csv
                loose_bb_test.csv
                loose_bb_train.csv
                loose_landmark_test.csv
                loose_landmark_train.csv
                attributes/
                    01-Male.txt
                    02-Black_Hair.txt
                    ...
            test/
                n000001/
                    0001_01.jpg
                    0002_01.jpg
                    ...
                n000009/
                ...
            train/
                n000002/
                    0001_01.jpg
                    ...
                n000003/
                ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    label_path = os.path.join(root_path, "label")
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    all_classifications = _get_classifications(
        label_path, dataset.catalog.classification.attributes.keys()
    )

    classification_subcatalog = dataset.catalog.classification
    for classification in all_classifications.values():
        classification_subcatalog.add_category(classification.category)

    all_box2ds = _get_box2ds(label_path)
    all_keypoint2ds = _get_keypoint2ds(label_path)

    for segment_name in _SEGMENT_NAMES:
        segment = dataset.create_segment(segment_name)
        with open(os.path.join(root_path, f"{segment_name}_list.txt"), encoding="utf-8") as fp:
            # The normal format of each line of the file is
            # n000001/0001_01.jpg
            # n000001/0002_01.jpg
            # n000001/0003_01.jpg
            # ...
            for line in fp:
                data = _get_data(
                    root_path,
                    segment_name,
                    line.rstrip("\n"),
                    all_classifications=all_classifications,
                    all_box2ds=all_box2ds,
                    all_keypoint2ds=all_keypoint2ds,
                )
                segment.append(data)
    return dataset


def _get_data(
    root_path: str,
    segment_name: str,
    image_path: str,
    *,
    all_classifications: Dict[str, Classification],
    all_box2ds: Dict[str, LabeledBox2D],
    all_keypoint2ds: Dict[str, LabeledKeypoints2D],
) -> Data:
    category_id, filename = image_path.split("/", 1)
    name_id = image_path.rstrip(".jpg")
    data = Data(os.path.join(root_path, segment_name, category_id, filename))
    data.label.classification = all_classifications[category_id]
    data.label.box2d = [all_box2ds[name_id]]
    data.label.keypoints2d = [all_keypoint2ds[name_id]]

    return data


def _get_classifications(
    label_path: str,
    attribute_names: Tuple[str, ...],
) -> Dict[str, Classification]:
    all_classifications = {}
    with open(os.path.join(label_path, "identity_meta.csv"), encoding="utf-8") as fp:
        # The normal format of each line of the file is
        # Class_ID, Name, Sample_Num, Flag, Gender,
        # n000001, "14th_Dalai_Lama",424,0, m,
        # n000002, "A_Fine_Frenzy",315,1, f,
        # n000003, "A._A._Gill",205,1, m,
        # ...
        for line in islice(csv.reader(fp), 1, None):
            # The normal format of each line of the file is
            # '<class_id>,"<class_name>",<sample_num>,<flag>,<gender>,\n'
            # but now there is an error type
            # '<class_id>,"<class_,name>",<sample_num>,<flag>,<gender>\n'
            if line[-1] != "":
                # join the splitted "class_ and name"
                line[1] = "".join(islice(line, 1, 3))
                # Starting from the 4th element, each element moves forward one step
                line.pop(2)
                line[4] = line[4].rstrip("\n")
            category_id = line[0]
            category_name = line[1].strip('"')
            attributes = dict(
                zip(
                    attribute_names,
                    (
                        int(line[2]),
                        bool(int(line[3])),
                        line[4],
                    ),
                )
            )
            all_classifications[category_id] = Classification(
                category=category_name,
                attributes=attributes,
            )
    return all_classifications


def _get_box2ds(label_path: str) -> Dict[str, LabeledBox2D]:
    all_box2d_attributes: DefaultDict[str, AttributeType] = defaultdict(dict)
    # The normal format of each line of the file is
    # n000002/0032_01.jpg	0
    # n000002/0039_01.jpg	0
    # n000002/0090_01.jpg	0
    # ...
    for file_path in glob(os.path.join(label_path, "attributes", "*.txt")):
        attribute_name = os.path.basename(file_path).rstrip(".txt").split("-", 1)[1]
        with open(file_path, encoding="utf-8") as fp:
            for line in fp:
                name, attribute_value = line.rstrip("\n").split("\t", 1)
                all_box2d_attributes[name.rstrip(".jpg")][attribute_name] = bool(
                    int(attribute_value)
                )
    all_boxes = {}
    for file_path in (
        os.path.join(label_path, "loose_bb_test.csv"),
        os.path.join(label_path, "loose_bb_train.csv"),
    ):
        # The normal format of each line of the file is
        # NAME_ID,X,Y,W,H
        # "n000001/0001_01",60,60,79,109
        # "n000001/0002_01",134,81,207,295
        # "n000001/0003_01",58,32,75,103
        # ...
        with open(file_path, encoding="utf-8") as fp:
            for row in islice(csv.reader(fp), 1, None):
                name_id = row.pop(0).strip('"')
                box = LabeledBox2D.from_xywh(*map(float, row))
                box2d_attribute = all_box2d_attributes.get(name_id)
                if box2d_attribute:
                    box.attributes = box2d_attribute
                all_boxes[name_id] = box

    return all_boxes


def _get_keypoint2ds(label_path: str) -> Dict[str, LabeledKeypoints2D]:
    all_keypoint2ds = {}
    for file_path in (
        os.path.join(label_path, "loose_landmark_test.csv"),
        os.path.join(label_path, "loose_landmark_train.csv"),
    ):
        # The normal format of each line of the file is
        # NAME_ID,P1X,P1Y,P2X,P2Y,P3X,P3Y,P4X,P4Y,P5X,P5Y
        # "n000001/0001_01",75.81253,110.2077,103.1778,104.6074,...
        # "n000001/0002_01",194.9206,211.5826,278.5339,206.3202,...
        # "n000001/0003_01",80.4145,74.07401,111.7425,75.42367,...
        # ...
        with open(file_path, encoding="utf-8") as fp:
            for row in islice(csv.reader(fp), 1, None):
                name_id = row.pop(0).strip('"')
                all_keypoint2ds[name_id] = LabeledKeypoints2D(chunked(map(float, row), 2))

    return all_keypoint2ds
