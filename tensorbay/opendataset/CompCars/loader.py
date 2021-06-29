#!/usr/bin/env python3
#
# Copytright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import csv
import os
from typing import Dict, List, Union

from ...dataset import Data, Dataset
from ...label import Box2DSubcatalog, LabeledBox2D

DATASET_NAME = "CompCars"


def CompCars(path: str) -> Dataset:
    """Dataloader of the `CompCars`_ dataset.

    .. _CompCars: http://mmlab.ie.cuhk.edu.hk/datasets/comp_cars/index.html

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

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.join(os.path.abspath(os.path.expanduser(path)), "data")

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    model_to_attributes = _extract_attributes(
        os.path.join(root_path, "misc", "attributes.txt"),
        dataset.catalog.box2d,
    )

    for mode in ("test", "train"):
        segment = dataset.create_segment(mode)
        segment_split_file = os.path.join(
            root_path, "train_test_split", "classification", f"{mode}.txt"
        )

        with open(segment_split_file, encoding="utf-8") as fp:
            # one line of segment split file looks like:
            # "78/1/2014/3ac218c0c6c378.jpg\n"
            # 78 is make name id, 1 is model name id, 2014 is release year
            for line in fp:
                image_path = os.path.join(root_path, "image", line.strip())

                # some image file names in segment split file do not exist in image folder
                if not os.path.exists(image_path):
                    continue

                data = Data(image_path)

                label_path = os.path.join(root_path, "label", f"{os.path.splitext(line)[0]}.txt")
                data.label.box2d = _create_box_label(
                    label_path, dataset.catalog.box2d, model_to_attributes
                )

                segment.append(data)

    return dataset


def _extract_attributes(
    path: str, box2d_subcatalog: Box2DSubcatalog
) -> Dict[str, Dict[str, Union[int, float, str, None]]]:
    attributes = {}

    model_names = box2d_subcatalog.attributes["model_name"].enum
    car_types = box2d_subcatalog.attributes["car_type"].enum

    with open(path, encoding="utf-8", newline="") as fp:
        # attributes file looks like:
        # model_id maximum_speed displacement door_number seat_number type
        #     1         235          1.8          5           5        4
        # ...
        reader = csv.DictReader(fp, delimiter=" ")
        for row in reader:
            attributes[row["model_id"]] = {
                "model_name": model_names[int(row["model_id"]) - 1],
                "maximum_speed": int(row["maximum_speed"]),
                "displacement": float(row["displacement"]),
                "door_number": int(row["door_number"]),
                "seat_number": int(row["seat_number"]),
                "car_type": car_types[int(row["type"])],
            }

    return attributes


def _create_box_label(
    label_path: str,
    box2d_subcatalog: Box2DSubcatalog,
    model_to_attributes: Dict[str, Dict[str, Union[int, float, str, None]]],
) -> List[LabeledBox2D]:
    # label_path looks like:
    # <root_path>/<make_name_id>/<model_name_id>/<release_year>/<file_name>.txt
    _, make_id, model_id, release_year, _ = label_path.rsplit(os.sep, 4)

    with open(label_path, encoding="utf-8") as fp:
        viewpoint_id = int(fp.readline().strip())
        viewpoint_index = viewpoint_id if viewpoint_id == -1 else viewpoint_id - 1

        attributes = model_to_attributes[model_id].copy()

        attributes["released_year"] = int(release_year) if release_year != "unknown" else None
        attributes["viewpoint"] = box2d_subcatalog.attributes["viewpoint"].enum[viewpoint_index]

        fp.readline()

        category = box2d_subcatalog.categories[int(make_id) - 1].name
        box2d_label = [
            LabeledBox2D(*map(int, line.strip().split()), category=category, attributes=attributes)
            for line in fp
        ]

    return box2d_label
