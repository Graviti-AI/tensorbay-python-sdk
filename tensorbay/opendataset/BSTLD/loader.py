#!/usr/bin/env python3
#
# Copytright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of the BSTLD dataset."""

import os

from ...dataset import Data, Dataset
from ...label import LabeledBox2D

DATASET_NAME = "BSTLD"

_LABEL_FILENAME_DICT = {
    "test": "test.yaml",
    "train": "train.yaml",
    "additional": "additional_train.yaml",
}


def BSTLD(path: str) -> Dataset:
    """Dataloader of the BSTLD dataset.

    Arguments:
        path: The root directory of the dataset.
            The file structure should be like::

                <path>
                    rgb/
                        additional/
                            2015-10-05-10-52-01_bag/
                                <image_name>.jpg
                                ...
                            ...
                        test/
                            <image_name>.jpg
                            ...
                        train/
                            2015-05-29-15-29-39_arastradero_traffic_light_loop_bag/
                                <image_name>.jpg
                                ...
                            ...
                    test.yaml
                    train.yaml
                    additional_train.yaml

    Returns:
        Loaded `Dataset` object.

    """
    import yaml  # pylint: disable=import-outside-toplevel

    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for mode, label_file_name in _LABEL_FILENAME_DICT.items():
        segment = dataset.create_segment(mode)
        label_file_path = os.path.join(root_path, label_file_name)

        with open(label_file_path, encoding="utf-8") as fp:
            labels = yaml.load(fp, yaml.FullLoader)

        for label in labels:
            if mode == "test":
                # the path in test label file looks like:
                # /absolute/path/to/<image_name>.png
                file_path = os.path.join(root_path, "rgb", "test", label["path"].rsplit("/", 1)[-1])
            else:
                # the path in label file looks like:
                # ./rgb/additional/2015-10-05-10-52-01_bag/<image_name>.png
                file_path = os.path.join(root_path, *label["path"][2:].split("/"))
            data = Data(file_path)
            data.label.box2d = [
                LabeledBox2D(
                    box["x_min"],
                    box["y_min"],
                    box["x_max"],
                    box["y_max"],
                    category=box["label"],
                    attributes={"occluded": box["occluded"]},
                )
                for box in label["boxes"]
            ]
            segment.append(data)

    return dataset
