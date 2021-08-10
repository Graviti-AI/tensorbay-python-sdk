#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name, missing-module-docstring

import os
from typing import Any

from ...dataset import Data, Dataset
from ...exception import ModuleImportError
from ...label import LabeledBox2D

_SEGMENTS = ("extra", "test", "train")

DATASET_NAME = "SVHN"


def SVHN(path: str) -> Dataset:
    """Dataloader of SVHN open dataset.

    .. _SVHN: http://ufldl.stanford.edu/housenumbers

    The file structure should be like::

        <path>
            Cropped/
                extra_32x32.mat
                test_32x32.mat
                train_32x32.mat
            FullNumbers/
                extra/
                    116507.png
                    116508.png
                    ...
                    digitStruct.mat
                    see_bboxes.m
                test/
                train/

    Arguments:
        path: The root directory of the dataset.

    Raises:
        ModuleImportError: When the module "h5py" can not be found.

    Returns:
        Loaded :class: `~tensorbay.dataset.dataset.Dataset` instance.

    """
    try:
        from h5py import File  # pylint: disable=import-outside-toplevel
    except ModuleNotFoundError as error:
        raise ModuleImportError(module_name=error.name) from error

    root_path = os.path.join(os.path.abspath(os.path.expanduser(path)), "FullNumbers")
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name in _SEGMENTS:
        segment = dataset.create_segment(segment_name)
        file_path = os.path.join(root_path, segment_name)
        mat = File(os.path.join(file_path, "digitStruct.mat"))
        names = mat["digitStruct"]["name"]
        bboxes = mat["digitStruct"]["bbox"]
        for name, bbox in zip(names, bboxes):
            segment.append(_get_data(mat, name, bbox, file_path))
    return dataset


def _get_data(mat: Any, name: Any, bbox: Any, file_path: str) -> Data:
    image_path = "".join(chr(v[0]) for v in mat[name[0]])
    data = Data(os.path.join(file_path, image_path), target_remote_path=image_path.zfill(10))
    data.label.box2d = []
    mat_bbox = mat[bbox[0]]

    labeled_box = (
        {key: [value[0][0]] for key, value in mat_bbox.items()}
        if mat_bbox["label"].shape[0] == 1
        else {key: [mat[value[0]][0][0] for value in values] for key, values in mat_bbox.items()}
    )

    for x, y, w, h, e in zip(
        labeled_box["left"],
        labeled_box["top"],
        labeled_box["width"],
        labeled_box["height"],
        labeled_box["label"],
    ):
        data.label.box2d.append(
            LabeledBox2D.from_xywh(x, y, w, h, category="0" if e == 10 else str(int(e)))
        )
    return data
