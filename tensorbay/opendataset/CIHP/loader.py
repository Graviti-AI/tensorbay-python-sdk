#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name, missing-module-docstring

import os

from ...dataset import Data, Dataset
from ...label import InstanceMask, SemanticMask

DATASET_NAME = "CIHP"
_SEGMENTS_INFO = {"train": "Training", "val": "Validation", "test": "Testing"}


def CIHP(path: str) -> Dataset:
    """Dataloader of the `CIHP`_ dataset.

    .. _CIHP: https://github.com/Engineering-Course/CIHP_PGN

    The file structure should be like::

        <path>
            Testing/
                Images/
                    0000002.jpg
                    ...
                test_id.txt
            Training/
                Images/
                    0000006.jpg
                    ...
                Category_ids/
                    0000006.png
                    ...
                Instance_ids/
                    0000006.png
                    ...
                train_id.txt
            Validation/
                Images/
                    0000001.jpg
                    ...
                Category_ids/
                    0000001.png
                    ...
                Instance_ids/
                    0000001.png
                    ...
                val_id.txt

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.join(
        os.path.abspath(os.path.expanduser(path)), "instance-level_human_parsing"
    )

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name, segment_path in _SEGMENTS_INFO.items():
        segment = dataset.create_segment(segment_name)
        segment_abspath = os.path.join(root_path, segment_path)
        image_path = os.path.join(segment_abspath, "Images")
        with open(os.path.join(segment_abspath, f"{segment_name}_id.txt"), "r") as fp:
            if segment_name == "test":
                for filename in fp:
                    segment.append(Data(os.path.join(image_path, f"{filename.rstrip()}.jpg")))
            else:
                category_path = os.path.join(segment_abspath, "Category_ids")
                instance_path = os.path.join(segment_abspath, "Instance_ids")
                for filename in fp:
                    filename = filename.rstrip()
                    data = Data(os.path.join(image_path, f"{filename}.jpg"))
                    label = data.label
                    png_filename = f"{filename}.png"
                    label.semantic_mask = SemanticMask(os.path.join(category_path, png_filename))
                    label.instance_mask = InstanceMask(os.path.join(instance_path, png_filename))
                    segment.append(data)
    return dataset
