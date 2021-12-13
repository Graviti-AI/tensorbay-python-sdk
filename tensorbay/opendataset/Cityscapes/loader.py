#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of the CityscapesGTFine dataset."""

import json
import os
from glob import glob
from typing import List

from tensorbay.dataset import Data, Dataset
from tensorbay.label import InstanceMask, LabeledPolygon, SemanticMask

DATASET_NAME = "CityscapesGTFine"
_SEGMENT_NAMES = {"test", "train", "val"}


def CityscapesGTFine(path: str) -> Dataset:
    """`CityscapesGTFine <https://www.cityscapes-dataset.com/>`_ dataset.

    The file structure should be like::

        <path>
            leftImg8bit/
                test/
                    berlin/
                        berlin_000000_000019_leftImg8bit.png
                        ...
                    ...
                train/
                    aachen/
                        aachen_000000_000019_leftImg8bit.png
                        ...
                    ...
                val/
                    frankfurt/
                        frankfurt_000000_000019_leftImg8bit.png
                        ...
                    ...
                ...
            gtFine/
                test/
                    berlin/
                        berlin_000000_000019_gtFine_instanceIds.png
                        berlin_000000_000019_gtFine_labelIds.png
                        berlin_000000_000019_gtFine_polygons.json
                        ...
                    ...
                train/
                    aachen/
                        aachen_000000_000019_gtFine_instanceIds.png
                        aachen_000000_000019_gtFine_labelIds.png
                        aachen_000000_000019_gtFine_polygons.json
                        ...
                    ...
                val/
                    frankfurt/
                        frankfurt_000000_000019_gtFine_instanceIds.png
                        frankfurt_000000_000019_gtFine_labelIds.png
                        frankfurt_000000_000019_gtFine_polygons.json
                        ...
                    ...
            ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.join(os.path.abspath(os.path.expanduser(path)))

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name in _SEGMENT_NAMES:
        segment = dataset.create_segment(segment_name)
        for image_path in glob(os.path.join(root_path, "leftImg8bit", segment_name, "*", "*.png")):
            city = os.path.basename(image_path).split("_", 1)[0]
            image_prefix = os.path.basename(image_path).rsplit("_", 1)[0]
            label_dir = os.path.join(root_path, "gtFine", segment_name, city)
            data = Data(image_path)
            # get semantic mask and instance mask
            label = data.label
            label.semantic_mask = SemanticMask(
                os.path.join(label_dir, f"{image_prefix}_gtFine_labelIds.png")
            )
            label.instance_mask = InstanceMask(
                os.path.join(label_dir, f"{image_prefix}_gtFine_instanceIds.png")
            )
            # get polygons
            polygons: List[LabeledPolygon] = []
            with open(
                os.path.join(label_dir, f"{image_prefix}_gtFine_polygons.json"),
                encoding="utf-8",
            ) as fp:
                objects = json.load(fp)["objects"]
            for obj in objects:
                polygons.append(LabeledPolygon(obj["polygon"], category=obj["label"]))
            label.polygon = polygons

            segment.append(data)
    return dataset
