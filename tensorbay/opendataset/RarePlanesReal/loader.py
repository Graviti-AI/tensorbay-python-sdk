#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of RarePlanesReal dataset."""

import csv
import json
import os
from collections import defaultdict
from typing import DefaultDict, Dict, List, Tuple

from tensorbay.dataset import Data, Dataset
from tensorbay.label import Classification, LabeledPolygon
from tensorbay.opendataset._utility import glob
from tensorbay.utility import chunked

DATASET_NAME = "RarePlanesReal"
_SEGMENT_NAMES = ("train", "test")


def RarePlanesReal(path: str) -> Dataset:
    """`RarePlanesReal <https://www.cosmiqworks.org/RarePlanes/>`_ dataset.

    The folder structure should be like::

        <path>
            metadata_annotations/
                RarePlanes_Public_Metadata.csv
                RarePlanes_Test_Coco_Annotations_tiled.json
                RarePlanes_Train_Coco_Annotations_tiled.json
            test/
                PS-RGB_tiled/
                    105_104001003108D900_tile_47.png
                    ...
            train/
                PS-RGB_tiled/
                    100_1040010029990A00_tile_319.png
                    ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    catalog = dataset.catalog

    annotations_dir = os.path.join(root_path, "metadata_annotations")
    classification_attributes = _get_classification_attributes(
        os.path.join(annotations_dir, "RarePlanes_Public_Metadata.csv"),
        catalog.classification.attributes.keys(),
    )
    for segment_name in _SEGMENT_NAMES:
        segment = dataset.create_segment(segment_name)
        image_name_to_polygons = _get_polygon_labels(
            annotations_dir, segment_name, catalog.polygon.attributes.keys()
        )
        for image_path in glob(os.path.join(root_path, segment_name, "PS-RGB_tiled", "*.png")):
            data = Data(image_path)
            label = data.label
            filename = os.path.basename(image_path)
            image_id = filename.rsplit("_", 2)[0]
            label.polygon = image_name_to_polygons[filename]
            label.classification = Classification(attributes=classification_attributes[image_id])
            segment.append(data)
    return dataset


def _get_classification_attributes(
    metadata_path: str, classification_attribute_names: Tuple[str, ...]
) -> Dict[str, Dict[str, str]]:
    with open(metadata_path, encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        return {
            row["image_id"]: {name: row[name] for name in classification_attribute_names}
            for row in reader
        }


def _get_polygon_labels(
    annotations_dir: str, segment_name: str, polygon_attribute_names: Tuple[str, ...]
) -> DefaultDict[str, List[LabeledPolygon]]:
    label_path = os.path.join(
        annotations_dir, f"RarePlanes_{segment_name.capitalize()}_Coco_Annotations_tiled.json"
    )
    image_name_to_polygons: DefaultDict[str, List[LabeledPolygon]] = defaultdict(list)
    with open(label_path, encoding="utf-8") as fp:
        label_contents = json.load(fp)
    annotations, categories = label_contents["annotations"], label_contents["categories"]
    for annotation, category in zip(annotations, categories):
        attributes = {attribute: annotation[attribute] for attribute in polygon_attribute_names}
        attributes["canards"] = annotation["canards"] == "Yes"
        attributes["truncated"] = bool(annotation["truncated"])
        image_name_to_polygons[category["image_fname"]].append(
            LabeledPolygon(chunked(annotation["segmentation"][0], 2), attributes=attributes)
        )
    return image_name_to_polygons
