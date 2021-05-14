#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import os
from typing import Any, Dict, Iterator, Tuple

from ...dataset import Data, Dataset
from ...exception import ModuleImportError
from ...label import Classification, LabeledBox2D, LabeledKeypoints2D

DATASET_NAME = "FLIC"
_VALID_KEYPOINT_INDICES = [0, 1, 2, 3, 4, 5, 6, 9, 12, 13, 16]


def FLIC(path: str) -> Dataset:
    """Dataloader of the `FLIC`_ dataset.

    .. _FLIC: https://bensapp.github.io/flic-dataset.html

    The folder structure should be like::

        <path>
            exampls.mat
            images/
                2-fast-2-furious-00003571.jpg
                ...

    Arguments:
        path: The root directory of the dataset.

    Raises:
        ModuleImportError: When the module "scipy" can not be found.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    try:
        from scipy.io import loadmat  # pylint: disable=import-outside-toplevel
    except ModuleNotFoundError as error:
        raise ModuleImportError(error.name) from error  # type: ignore[arg-type]

    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = Dataset(DATASET_NAME)

    annotations = loadmat(os.path.join(root_path, "examples.mat"))["examples"][0]
    dataset.create_segment("train")
    dataset.create_segment("test")
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    # try whether the dataset has bad segment
    try:
        _ = annotations["isbad"]
        flag = True
        dataset.create_segment("bad")
        dataset.catalog.classification.add_attribute(name="isunchecked", type_="boolean")
    except ValueError:
        flag = False

    for data, segment_name in _get_data(root_path, annotations, flag):
        dataset[segment_name].append(data)

    return dataset


def _get_data(path: str, annotations: Any, flag: bool) -> Iterator[Tuple[Data, str]]:
    filepath_to_data: Dict[str, Data] = {}

    for annotation in annotations:
        filepath = annotation["filepath"][0]

        keypoints = LabeledKeypoints2D(
            annotation["coords"].T[_VALID_KEYPOINT_INDICES],
            attributes={"poselet_hit_idx": annotation["poselet_hit_idx"].T.tolist()},
        )
        box2d = LabeledBox2D(*annotation["torsobox"][0].tolist())

        if filepath not in filepath_to_data:
            data = Data(os.path.join(path, "images", filepath))
            data.label.keypoints2d = [keypoints]
            data.label.box2d = [box2d]
            attribute = {"currframe": int(annotation["currframe"][0][0])}

            if flag:
                attribute["isunchecked"] = bool(annotation["isunchecked"])
            data.label.classification = Classification(
                category=annotation["moviename"][0], attributes=attribute
            )
            filepath_to_data[filepath] = data

            if annotation["istrain"]:
                segment_name = "train"
            elif annotation["istest"]:
                segment_name = "test"
            else:
                segment_name = "bad"
            yield data, segment_name

        else:
            image_data = filepath_to_data[filepath]
            image_data.label.keypoints2d.append(keypoints)
            image_data.label.box2d.append(box2d)
