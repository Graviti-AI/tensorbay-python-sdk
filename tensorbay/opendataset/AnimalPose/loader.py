#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import json
import os
from typing import Iterable, Iterator, List, Tuple

from ...dataset import Data, Dataset
from ...exception import ModuleImportError
from ...geometry import Keypoint2D
from ...label import LabeledBox2D, LabeledKeypoints2D
from .._utility import glob

DATASET_NAME_5 = "AnimalPose5"
DATASET_NAME_7 = "AnimalPose7"

_KEYPOINT_TO_INDEX = {
    "L_Eye": 0,
    "R_Eye": 1,
    "Nose": 4,
    "L_EarBase": 2,
    "R_EarBase": 3,
    "Throat": 5,
    "L_F_Elbow": 8,
    "R_F_Elbow": 9,
    "L_F_Paw": 16,
    "R_F_Paw": 17,
    "Withers": 7,
    "TailBase": 6,
    "L_B_Paw": 18,
    "R_B_Paw": 19,
    "L_B_Elbow": 10,
    "R_B_Elbow": 11,
    "L_F_Knee": 12,
    "R_F_Knee": 13,
    "L_B_Knee": 14,
    "R_B_Knee": 15,
}


def AnimalPose5(path: str) -> Dataset:
    """Dataloader of the `5 Categories Animal-Pose`_ dataset.

    .. _5 Categories Animal-Pose: https://sites.google.com/view/animal-pose/

    The file structure should be like::

        <path>
            keypoint_image_part1/
                cat/
                    2007_000549.jpg
                    2007_000876.jpg
                    ...
                ...
            PASCAL2011_animal_annotation/
                cat/
                    2007_000549_1.xml
                    2007_000876_1.xml
                    2007_000876_2.xml
                    ...
                ...
            animalpose_image_part2/
                cat/
                    ca1.jpeg
                    ca2.jpeg
                    ...
                ...
            animalpose_anno2/
                cat/
                    ca1.xml
                    ca2.xml
                ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = Dataset(DATASET_NAME_5)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog_5.json"))
    animals = dataset.catalog.keypoints2d.categories.keys()

    for segment_name, _get_data in _DATA_GETTERS.items():
        segment = dataset.create_segment(segment_name)
        for data in _get_data(root_path, animals):
            segment.append(data)

    return dataset


def _get_data_part1(root_path: str, aniamls: Iterable[str]) -> Iterator[Data]:
    try:
        import xmltodict  # pylint: disable=import-outside-toplevel
    except ModuleNotFoundError as error:
        raise ModuleImportError(error.name) from error  # type: ignore[arg-type]

    for animal in aniamls:
        for image_path in glob(os.path.join(root_path, "keypoint_image_part1", animal, "*.jpg")):
            data = Data(image_path, target_remote_path=f"{animal}/{os.path.basename(image_path)}")

            for annotation_path in glob(
                os.path.join(
                    root_path,
                    "PASCAL2011_animal_annotation",
                    animal,
                    f"{os.path.splitext(os.path.basename(image_path))[0]}_*.xml",
                )
            ):

                with open(annotation_path, encoding="utf-8") as fp:
                    labels = xmltodict.parse(fp.read())

                box2d = labels["annotation"]["visible_bounds"]
                data.label.box2d = [
                    LabeledBox2D.from_xywh(
                        x=float(box2d["@xmin"]),
                        y=float(box2d["@ymin"]),
                        width=float(box2d["@width"]),
                        height=float(box2d["@height"]),
                        category=animal,
                    )
                ]

                keypoints2d: List[Tuple[float, float, int]] = [()] * 20  # type: ignore[list-item]
                for keypoint in labels["annotation"]["keypoints"]["keypoint"]:
                    keypoints2d[_KEYPOINT_TO_INDEX[keypoint["@name"]]] = (
                        float(keypoint["@x"]),
                        float(keypoint["@y"]),
                        int(keypoint["@visible"]),
                    )
                data.label.keypoints2d = [LabeledKeypoints2D(keypoints2d, category=animal)]

            yield data


def _get_data_part2(root_path: str, aniamls: Iterable[str]) -> Iterator[Data]:
    try:
        import xmltodict  # pylint: disable=import-outside-toplevel
    except ModuleNotFoundError as error:
        raise ModuleImportError(error.name) from error  # type: ignore[arg-type]

    for animal in aniamls:
        for image_path in glob(os.path.join(root_path, "animalpose_image_part2", animal, "*.jpeg")):
            data = Data(image_path, target_remote_path=f"{animal}/{os.path.basename(image_path)}")

            annotation_path = os.path.join(
                root_path,
                "animalpose_anno2",
                animal,
                f"{os.path.splitext(os.path.basename(image_path))[0]}.xml",
            )

            with open(annotation_path, encoding="utf-8") as fp:
                labels = xmltodict.parse(fp.read())

            box2d = labels["annotation"]["visible_bounds"]
            data.label.box2d = [
                LabeledBox2D.from_xywh(
                    x=float(box2d["@xmin"]),
                    y=float(box2d["@xmax"]),  # xmax means ymin in the annotation
                    width=float(box2d["@width"]),
                    height=float(box2d["@height"]),
                    category=animal,
                )
            ]

            keypoints2d = LabeledKeypoints2D(category=animal)
            for keypoint in labels["annotation"]["keypoints"]["keypoint"]:
                keypoints2d.append(  # pylint: disable=no-member
                    Keypoint2D(
                        float(keypoint["@x"]), float(keypoint["@y"]), int(keypoint["@visible"])
                    )
                )
            data.label.keypoints2d = [keypoints2d]
            yield data


_DATA_GETTERS = {"part1": _get_data_part1, "part2": _get_data_part2}


def AnimalPose7(path: str) -> Dataset:
    """Dataloader of `7 Categories Animal-Pose`_ dataset.

    .. _7 Categories Animal-Pose: https://sites.google.com/view/animal-pose/

    The file structure should be like::

        <path>
            bndbox_image/
                antelope/
                    Img-77.jpg
                    ...
                ...
            bndbox_anno/
                antelope.json
                ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        loaded :class:`~tensorbay.dataset.dataset.Dataset` object.

    """
    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = Dataset(DATASET_NAME_7)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog_7.json"))

    segment = dataset.create_segment()

    for animal in dataset.catalog.box2d.categories.keys():
        with open(os.path.join(root_path, "bndbox_anno", f"{animal}.json"), encoding="utf-8") as fp:
            annotations = json.load(fp)
        for image_name, box2ds in annotations.items():
            image_path = os.path.join(root_path, "bndbox_image", animal, image_name)
            data = Data(image_path, target_remote_path=f"{animal}/{image_name}")
            data.label.box2d = []

            for box2d in box2ds:
                coordinates = box2d["bndbox"]
                data.label.box2d.append(
                    LabeledBox2D(
                        float(coordinates["xmin"]),
                        float(coordinates["ymin"]),
                        float(coordinates["xmax"]),
                        float(coordinates["ymax"]),
                        category=animal,
                    )
                )

            segment.append(data)

    return dataset
