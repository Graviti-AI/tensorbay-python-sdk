#!/usr/bin/env python3
#
# Copytright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of RarePlanesSynthetic dataset."""

import os
from itertools import takewhile
from typing import Any, Callable, Dict, List, Tuple, Union

import numpy as np

from tensorbay.dataset import Data, Dataset
from tensorbay.label import Classification, LabeledBox2D, PanopticMask
from tensorbay.opendataset._utility import glob

try:
    from PIL import Image
except ModuleNotFoundError:
    from tensorbay.opendataset._utility.mocker import Image  # pylint:disable=ungrouped-imports
try:
    import xmltodict
except ModuleNotFoundError:
    from tensorbay.opendataset._utility.mocker import xmltodict  # pylint:disable=ungrouped-imports

DATASET_NAME = "RarePlanesSynthetic"
_MAX_CATEGORY_LEVEL = 6
_ATTRIBUTES_GETTER: Dict[Tuple[int, ...], Callable[[str], Union[int, str, float]]] = {
    (1, 3, 11, 13): float,
    (14, 15): lambda x: x,
    (12,): int,
}


def RarePlanesSynthetic(path: str) -> Dataset:
    """`RarePlanesSynthetic <https://www.cosmiqworks.org/RarePlanes/>`_ dataset.

    The file structure of RarePlanesSynthetic looks like::

        <path>
            images/
                Atlanta_Airport_0_0_101_1837.png
                ...
            masks/
                Atlanta_Airport_0_0_101_1837_mask.png
                ...
            xmls/
                Atlanta_Airport_0_0_101_1837.xml
                ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    category_ids = dataset.catalog.panoptic_mask.get_category_to_index()
    segment = dataset.create_segment()
    original_mask_dir = os.path.join(root_path, "masks")
    new_mask_dir = os.path.join(root_path, "new_masks")
    os.makedirs(new_mask_dir, exist_ok=True)
    annotation_dir = os.path.join(root_path, "xmls")
    for image_path in glob(os.path.join(root_path, "images", "*.png")):
        segment.append(
            _get_data(image_path, original_mask_dir, annotation_dir, new_mask_dir, category_ids)
        )
    return dataset


def _get_data(
    image_path: str,
    original_mask_dir: str,
    annotation_dir: str,
    new_mask_dir: str,
    category_ids: Dict[str, int],
) -> Data:
    stem = os.path.splitext(os.path.basename(image_path))[0]
    new_mask_path = os.path.join(new_mask_dir, f"{stem}.png")
    data = Data(image_path)
    label = data.label
    with open(os.path.join(annotation_dir, f"{stem}.xml"), encoding="utf-8") as fp:
        labels: Any = xmltodict.parse(fp.read())["image"]
    label.box2d, label.panoptic_mask = _get_box2d_and_panoptic_mask(
        labels["object"],
        os.path.join(original_mask_dir, f"{stem}_mask.png"),
        new_mask_path,
        category_ids,
    )
    label.classification = _get_classification(labels["JSON_Variation_Parameters"]["parameter"])
    return data


def _get_classification(classification_labels: List[Dict[str, str]]) -> Classification:
    attributes: Dict[str, Union[int, float, str]] = {}
    for indices, attribute_getter in _ATTRIBUTES_GETTER.items():
        for index in indices:
            classification_label = classification_labels[index]
            attributes[classification_label["@name"]] = attribute_getter(
                classification_label["@value"]
            )
    return Classification(attributes=attributes)


def _get_box2d_and_panoptic_mask(
    objects: Any,
    original_mask_path: str,
    new_mask_path: str,
    category_ids: Dict[str, int],
) -> Tuple[List[LabeledBox2D], PanopticMask]:
    all_category_ids: Dict[int, int] = {}
    original_mask = np.array(Image.open(original_mask_path))
    box2ds: List[LabeledBox2D] = []
    if not isinstance(objects, list):
        objects = [objects]
    rgba_to_instance_id: Dict[Tuple[int, ...], int] = {}
    for index, obj in enumerate(objects, 1):
        category = ".".join(
            takewhile(bool, (obj.get(f"category{i}", "") for i in range(_MAX_CATEGORY_LEVEL)))
        )
        bndbox = obj["bndbox2D"]
        box2ds.append(
            LabeledBox2D(
                int(bndbox["xmin"]),
                int(bndbox["ymin"]),
                int(bndbox["xmax"]),
                int(bndbox["ymax"]),
                category=category,
                attributes={"focus_blur": bndbox["focus_blur"]},
            )
        )
        rgba_to_instance_id[tuple(map(int, obj["object_mask_color_rgba"].split(",")))] = index
        all_category_ids[index] = category_ids[category]
    mask = np.vectorize(lambda r, g, b: rgba_to_instance_id.get((r, g, b, 255), 0))(
        original_mask[:, :, 0], original_mask[:, :, 1], original_mask[:, :, 2]
    ).astype(np.uint8)
    Image.fromarray(mask).save(new_mask_path)
    panoptic_mask = PanopticMask(new_mask_path)
    panoptic_mask.all_category_ids = all_category_ids
    return box2ds, panoptic_mask
