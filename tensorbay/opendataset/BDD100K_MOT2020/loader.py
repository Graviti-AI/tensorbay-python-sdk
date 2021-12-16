#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#
# pylint: disable=invalid-name

"""Dataloaders of BDD100K_MOTS2020 dataset and BDD100K_MOT2020 dataset."""


import json
import os
from typing import Any, Callable, Dict, Iterable

import numpy as np

from tensorbay.dataset import Data, Dataset
from tensorbay.label import InstanceMask, LabeledBox2D, LabeledMultiPolygon, SemanticMask
from tensorbay.opendataset._utility import glob

try:
    from PIL import Image
except ModuleNotFoundError:
    from tensorbay.opendataset._utility.mocker import Image  # pylint:disable=ungrouped-imports

DATASET_NAMES = {
    "mots": "BDD100K_MOTS2020",
    "mot": "BDD100K_MOT2020",
}
_SEGMENT_NAMES = ("train", "val", "test")
_TRACKING_DATASET_INFO = {
    "mots": ("bdd100k_seg_track_20", "seg_track_20"),
    "mot": ("bdd100k_box_track_20", ""),
}
_DATA_GENERATOR = Callable[[str, str, str, str, str], Iterable[Data]]


def BDD100K_MOTS2020(path: str) -> Dataset:
    """`BDD100K_MOTS2020 <https://bdd-data.berkeley.edu>`_ dataset.

    The file structure should be like::

        <path>
            bdd100k_seg_track_20/
                images/
                    seg_track_20/
                        test/
                            cabc30fc-e7726578/
                                cabc30fc-e7726578-0000001.jpg
                                ...
                            ...
                        train/
                            000d4f89-3bcbe37a/
                                000d4f89-3bcbe37a-0000001.jpg
                                ...
                            ...
                        val/
                            b1c9c847-3bda4659/
                                b1c9c847-3bda4659-0000001.jpg
                                ...
                            ...
                labels/
                    seg_track_20/
                        bitmasks/
                            train/
                                000d4f89-3bcbe37a/
                                    000d4f89-3bcbe37a-0000001.png
                                    ...
                                ...
                            val/
                                b1c9c847-3bda4659/
                                    b1c9c847-3bda4659-0000001.png
                                    ...
                                ...
                        polygons/
                            train/
                                000d4f89-3bcbe37a.json
                                ...
                            val/
                                b1c9c847-3bda4659.json
                                ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    return _tracking_loader(path, "mots")


def BDD100K_MOT2020(path: str) -> Dataset:
    """`BDD100K_MOT2020 <https://bdd-data.berkeley.edu>`_ dataset.

    The file structure should be like::

        <path>
            bdd100k_box_track_20/
                images/
                    train/
                        00a0f008-3c67908e/
                            00a0f008-3c67908e-0000001.jpg
                            ...
                        ...
                    val/
                        b1c9c847-3bda4659/
                            b1c9c847-3bda4659-0000001.jpg
                            ...
                        ...
                    test/
                        cabc30fc-e7726578/
                            cabc30fc-e7726578-0000001.jpg
                            ...
                        ...
                labels/
                    train/
                        00a0f008-3c67908e.json
                        ...
                    val/
                        b1c9c847-3bda4659.json
                        ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    return _tracking_loader(path, "mot")


def _tracking_loader(path: str, tracking_type: str) -> Dataset:
    tracking_dataset_info = _TRACKING_DATASET_INFO[tracking_type]
    root_path = os.path.join(os.path.abspath(os.path.expanduser(path)), tracking_dataset_info[0])
    dataset = Dataset(DATASET_NAMES[tracking_type])
    dataset.notes.is_continuous = True
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), f"catalog_{tracking_type}.json"))
    images_dir = os.path.join(root_path, "images", tracking_dataset_info[1])
    labels_dir = os.path.join(root_path, "labels", tracking_dataset_info[1])
    _load_tracking_segment(dataset, images_dir, labels_dir, tracking_type)

    return dataset


def _load_tracking_segment(
    dataset: Dataset,
    images_dir: str,
    labels_dir: str,
    tracking_type: str,
) -> None:
    for segment_prefix in _SEGMENT_NAMES:
        image_subdirs = glob(os.path.join(images_dir, segment_prefix, "*"))
        segment_labels_dir = os.path.join(labels_dir, "polygons", segment_prefix)
        original_mask_dir = os.path.join(labels_dir, "bitmasks", segment_prefix)
        mask_dir = os.path.join(labels_dir, "single_channel_masks", segment_prefix)
        os.makedirs(mask_dir, exist_ok=True)

        if segment_prefix == "test":
            generate_data: _DATA_GENERATOR = _generate_test_data
        else:
            generate_data = _generate_data
        for image_subdir in image_subdirs:
            segment = dataset.create_segment(f"{segment_prefix}_{os.path.basename(image_subdir)}")
            segment.extend(
                generate_data(
                    image_subdir,
                    segment_labels_dir,
                    original_mask_dir,
                    mask_dir,
                    tracking_type,
                )
            )


def _generate_test_data(image_subdir: str, _: str, __: str, ___: str, ____: str) -> Iterable[Data]:
    yield from map(Data, glob(os.path.join(image_subdir, "*.jpg")))


def _generate_data(
    image_subdir: str,
    segment_labels_dir: str,
    original_mask_dir: str,
    mask_dir: str,
    tracking_type: str,
) -> Iterable[Data]:
    subdir_name = os.path.basename(image_subdir)
    if tracking_type == "mots":
        original_mask_subdir = os.path.join(original_mask_dir, subdir_name)
        mask_subdir = os.path.join(mask_dir, subdir_name)
        semantic_subdir = os.path.join(mask_subdir, "semantic")
        instance_subdir = os.path.join(mask_subdir, "instance")
        os.makedirs(semantic_subdir, exist_ok=True)
        os.makedirs(instance_subdir, exist_ok=True)
    with open(os.path.join(segment_labels_dir, f"{subdir_name}.json"), encoding="utf-8") as fp:
        label_contents = json.load(fp)
    for label_content in label_contents:
        label_content_name = label_content["name"]
        if "/" in label_content_name:
            label_content_name = label_content_name[len(label_content["videoName"]) + 1 :]
        image_path = os.path.join(image_subdir, label_content_name)
        yield _get_mot_data(
            image_path, label_content
        ) if tracking_type == "mot" else _get_mots_data(
            image_path,
            original_mask_subdir,
            semantic_subdir,
            instance_subdir,
            os.path.splitext(label_content_name)[0],
            label_content=label_content,
        )


def _get_mot_data(image_path: str, label_content: Dict[str, Any]) -> Data:
    data = Data(image_path)
    labeled_box2ds = []
    for label_info in label_content.get("labels", ()):
        box2d_info = label_info.get("box2d")
        if not box2d_info:
            continue
        labeled_box2d = LabeledBox2D(
            box2d_info["x1"],
            box2d_info["y1"],
            box2d_info["x2"],
            box2d_info["y2"],
            category=label_info["category"],
            attributes=label_info["attributes"],
            instance=label_info["id"],
        )
        labeled_box2ds.append(labeled_box2d)
    data.label.box2d = labeled_box2ds

    return data


def _get_mots_data(
    image_path: str,
    original_mask_subdir: str,
    semantic_subdir: str,
    instance_subdir: str,
    stem: str,
    *,
    label_content: Dict[str, Any],
) -> Data:
    data = Data(image_path)
    labeled_multipolygons = []
    for label_info in label_content.get("labels", ()):
        if "poly2d" not in label_info:
            continue
        labeled_multipolygon = LabeledMultiPolygon(
            polygons=(poly2d_info["vertices"] for poly2d_info in label_info["poly2d"]),
            category=label_info["category"],
            attributes=label_info["attributes"],
            instance=str(label_info["id"]),
        )
        labeled_multipolygons.append(labeled_multipolygon)

    semantic_path = os.path.join(semantic_subdir, f"{stem}.png")
    instance_path = os.path.join(instance_subdir, f"{stem}.png")
    mask_info = _save_and_get_mask_info(
        os.path.join(original_mask_subdir, f"{stem}.png"),
        semantic_path,
        instance_path,
        os.path.join(instance_subdir, f"{stem}.json"),
    )
    ins_mask = InstanceMask(instance_path)
    ins_mask.all_attributes = mask_info["all_attributes"]

    label = data.label
    label.multi_polygon = labeled_multipolygons
    label.semantic_mask = SemanticMask(semantic_path)
    label.instance_mask = ins_mask
    return data


def _save_and_get_mask_info(
    original_mask_path: str, semantic_path: str, instance_path: str, mask_info_path: str
) -> Dict[str, Any]:
    if not os.path.exists(instance_path):
        mask = np.array(Image.open(original_mask_path), dtype=np.uint16)
        all_attributes = {}
        for _, attributes, instance_id_high, instance_id_low in np.unique(
            np.reshape(mask, (-1, 4)), axis=0
        ):
            # the instance_id is represented by 2 channels, instance_id = high*256+low
            instance_id = int(instance_id_low + (instance_id_high << 8))
            all_attributes[instance_id] = {
                "truncated": bool(attributes & 8),
                "occluded": bool(attributes & 4),
                "crowd": bool(attributes & 2),
                "ignore": bool(attributes & 1),
            }
        mask_info = {"all_attributes": all_attributes}
        with open(mask_info_path, "w", encoding="utf-8") as fp:
            json.dump(mask_info, fp)
        Image.fromarray(mask[:, :, -1] + (mask[:, :, -2] << 8)).save(instance_path)
        if not os.path.exists(semantic_path):
            Image.fromarray(mask[:, :, 0]).save(semantic_path)
    else:
        if not os.path.exists(semantic_path):
            Image.fromarray(np.array(Image.open(original_mask_path))[:, :, 0]).save(semantic_path)
        with open(mask_info_path, encoding="utf-8") as fp:
            mask_info = json.load(
                fp,
                object_hook=lambda info: {
                    int(key) if key.isdigit() else key: value for key, value in info.items()
                },
            )
    return mask_info
