#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of OxfordIIITPet dataset."""

import os
from typing import Any, List

from tensorbay.dataset import Data, Dataset
from tensorbay.label import Classification, LabeledBox2D, SemanticMask
from tensorbay.opendataset._utility.glob import glob

try:
    import xmltodict
except ModuleNotFoundError:
    from tensorbay.opendataset._utility.mocker import xmltodict  # pylint:disable=ungrouped-imports

DATASET_NAME = "OxfordIIITPet"


def OxfordIIITPet(path: str) -> Dataset:
    """`OxfordIIITPet <https://www.robots.ox.ac.uk/~vgg/data/pets/>`_ dataset.

    The file structure should be like::

        <path>
            annotations/
                trimaps/
                    Bombay_113.png
                    Bombay_114.png
                    ...
                xmls/
                    Birman_174.xml
                    Birman_175.xml
                    ...
                list.txt
                test.txt
                trainval.txt
                README
            images/
                Bombay_117.jpg
                Bombay_118.jpg
                ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class: `~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    trainval_segment = dataset.create_segment("trainval")
    test_segment = dataset.create_segment("test")
    annotation_path = os.path.join(root_path, "annotations")
    for image_path in glob(os.path.join(root_path, "images", "*.jpg")):
        stem = os.path.splitext(os.path.basename(image_path))[0]
        name = "Cat" if stem.istitle() else "Dog"
        category, num = stem.rsplit("_", 1)
        data = Data(image_path, target_remote_path=f"{category}_{num.zfill(3)}.jpg")
        label = data.label
        label.classification = Classification(category=f"{name}.{category}")
        label.semantic_mask = SemanticMask(os.path.join(annotation_path, "trimaps", f"{stem}.png"))
        xml_path = os.path.join(annotation_path, "xmls", f"{stem}.xml")
        if os.path.exists(xml_path):
            label.box2d = _get_box_label(xml_path)
            trainval_segment.append(data)
        else:
            test_segment.append(data)
    return dataset


def _get_box_label(file_path: str) -> List[LabeledBox2D]:
    with open(file_path, encoding="utf-8") as fp:
        labels: Any = xmltodict.parse(fp.read())

    objects = labels["annotation"]["object"]
    if not isinstance(objects, list):
        objects = [objects]
    box2d = []
    for obj in objects:
        bndbox = obj["bndbox"]
        box2d.append(
            LabeledBox2D(
                float(bndbox["xmin"]),
                float(bndbox["ymin"]),
                float(bndbox["xmax"]),
                float(bndbox["ymax"]),
            )
        )
    return box2d
