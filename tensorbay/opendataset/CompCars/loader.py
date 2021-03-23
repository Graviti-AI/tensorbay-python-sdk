#!/usr/bin/env python3
#
# Copytright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of the CompCars dataset."""

import os
from typing import Any, Dict, List, Tuple

from ...dataset import Data, Dataset
from ...label import AttributeInfo, Classification, LabeledBox2D
from ...utility import NameOrderedDict

DATASET_NAME = "CompCars"

_SEGMENT_SPLIT_FILES = (
    ("test", os.path.join("data", "train_test_split", "classification", "test.txt")),
    ("train", os.path.join("data", "train_test_split", "classification", "train.txt")),
)


def CompCars(path: str) -> Dataset:
    """Dataloader of the CompCars dataset.

    Arguments:
        path: The root path of dataset.
            The file structure should be like::

                <path>
                    data/
                        image/
                            <make name id>/
                                <model name id>/
                                    <year>/
                                        <image name>.jpg
                                        ...
                                    ...
                                ...
                            ...
                        label/
                            <make name id>/
                                <model name id>/
                                    <year>/
                                        <image name>.txt
                                        ...
                                    ...
                                ...
                            ...
                        misc/
                            attributes.txt
                            car_type.mat
                            make_model_name.mat
                        train_test_split/
                            classification/
                                train.txt
                                test.txt

    Returns:
        Loaded `Dataset` object.

    """
    root_path = os.path.join(os.path.abspath(os.path.expanduser(path)), "data")

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    model_to_attributes = _get_model_to_attributes(
        os.path.join(root_path, "misc", "attributes.txt"),
        dataset.catalog.classification.attributes,
    )

    classification_categories = tuple(dataset.catalog.classification.categories)
    box_categories = tuple(dataset.catalog.box2d.categories)

    for mode, segment_split_file in _SEGMENT_SPLIT_FILES:
        segment = dataset.create_segment(mode)
        with open(os.path.join(root_path, segment_split_file), encoding="utf-8") as fp:
            # one line of segment split file looks like:
            # "78/1/2014/3ac218c0c6c378.jpg\n"
            # 78 is make name id, 1 is model name id, 2014 is release year
            for image_file_name in fp:
                image_path = os.path.join(root_path, "image", *image_file_name.strip().split("/"))
                # some image file names in segment split file do not exist in image folder
                if not os.path.exists(image_path):
                    continue
                label_path = os.path.join(
                    root_path, "label", *(os.path.splitext(image_file_name)[0] + ".txt").split("/")
                )
                data = Data(image_path)
                data.label.classification = _create_classification_label(
                    image_path, model_to_attributes, classification_categories
                )
                data.label.box2d = _create_box_label(label_path, box_categories)
                segment.append(data)

    return dataset


def _get_model_to_attributes(
    path: str, classification_attributes: NameOrderedDict[AttributeInfo]
) -> Dict[str, Dict[str, Any]]:
    attributes = {}

    model_names = classification_attributes["model_name"].enum
    car_types = classification_attributes["car_type"].enum

    with open(path, encoding="utf-8") as fp:
        # attributes file looks like:
        # model_id maximum_speed displacement door_number seat_number type
        #     1         235          1.8          5           5        4
        # ...
        fp.readline()
        for line in fp:
            line_split = line.strip().split()
            attributes_values = (
                model_names[int(line_split[0]) - 1],
                int(line_split[1]),
                float(line_split[2]),
                int(line_split[3]),
                int(line_split[4]),
                car_types[int(line_split[5])],
            )
            attributes[line_split[0]] = dict(zip(classification_attributes, attributes_values))

    return attributes


def _create_box_label(label_path: str, categories: Tuple[str, ...]) -> List[LabeledBox2D]:
    with open(label_path, encoding="utf-8") as fp:
        viewpoint_id = int(fp.readline().strip())
        viewpoint_index = viewpoint_id if viewpoint_id == -1 else viewpoint_id - 1

        fp.readline()

        category = categories[viewpoint_index]
        box2d = [LabeledBox2D(*map(int, line.strip().split()), category=category) for line in fp]

    return box2d


def _create_classification_label(
    image_path: str,
    model_to_attributes: Dict[str, Dict[str, Any]],
    categories: Tuple[str, ...],
) -> Classification:
    # image_path looks like:
    # <root_path>/<make_name_id>/<model_name_id>/<release_year>/<file_name>.jpg"
    image_path_split = image_path.rsplit(os.sep, 4)

    value = model_to_attributes.get(image_path_split[-3])
    if value:
        attributes = value.copy()
        released_year = image_path_split[-2]
        attributes["released_year"] = int(released_year) if released_year != "unknown" else None

    return Classification(category=categories[int(image_path_split[-4]) - 1], attributes=attributes)
