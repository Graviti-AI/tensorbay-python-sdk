#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#
# pylint: disable=invalid-name

"""This file defines the BDD100K dataloader."""

import json
import os
from typing import Any, Callable, Dict, Iterable, List
from warnings import warn

import numpy as np

from ...dataset import Data, Dataset
from ...label import (
    Classification,
    InstanceMask,
    LabeledBox2D,
    LabeledMultiPolygon,
    LabeledPolygon,
    LabeledPolyline2D,
    PanopticMask,
    SemanticMask,
)
from .._utility import glob

try:
    from PIL import Image
except ModuleNotFoundError:
    from .._utility.mocker import Image

DATASET_NAMES = {
    "100k": "BDD100K",
    "10k": "BDD100K_10K",
    "mots": "BDD100K_MOTS2020",
    "mot": "BDD100K_MOT2020",
}
_SEGMENT_NAMES = ("train", "val", "test")
_LABEL_TYPE_INFO_100K = {
    "det": ("Detection 2020", "BOX2D"),
    "lane": ("Lane Marking", "POLYLINE2D"),
    "drivable": ("Drivable Area", "POLYGON"),
}
_SEGMENTATIONS_INFO = {
    "sem": ("sem_seg", "masks"),
    "ins": ("ins_seg", "bitmasks"),
    "pan": ("pan_seg", "bitmasks"),
}
_TRACKING_DATASET_INFO = {
    "mots": ("bdd100k_seg_track_20", "seg_track_20"),
    "mot": ("bdd100k_box_track_20", ""),
}
_DATA_GENERATOR = Callable[[str, str, str, str, str], Iterable[Data]]


def BDD100K(path: str) -> Dataset:
    """Load BDD100K Dataset to Tensorbay.

    The file structure should be like::

        <path>
            bdd100k_images_100k/
                images/
                    100k/
                        test
                        train
                        val
                labels/
                    det_20/
                        det_train.json
                        det_val.json
                    lane/
                        polygons/
                            lane_train.json
                            lane_val.json
                    drivable/
                        polygons/
                            drivable_train.json
                            drivable_val.json

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    return _BDD100K_loader(path, "100k")


def _BDD100K_10K(path: str) -> Dataset:
    """Load a sub-dataset 10k of BDD100K Dataset to Tensorbay.

    The dataset is named as 'BDD100K_10K'

    The file structure should be like::

        <path>
            bdd100k_images_10k/
                images/
                    10k/
                        test/
                            cabc30fc-e7726578.jpg
                            ...
                        train/
                            0a0a0b1a-7c39d841.jpg
                            ...
                        val/
                            b1c9c847-3bda4659.jpg
                            ...
                labels/
                    pan_seg/
                        polygons/
                            pan_seg_train.json
                            pan_seg_val.json
                        bitmasks/
                            train/
                                0a0a0b1a-7c39d841.png
                                ...
                            val/
                                b1c9c847-3bda4659.png
                                ...
                    sem_seg/
                        masks/
                            train/
                                0a0a0b1a-7c39d841.png
                                ...
                            val/
                                b1c9c847-3bda4659.png
                                ...
                    ins_seg/
                        bitmasks/
                            train/
                                0a0a0b1a-7c39d841.png
                                ...
                            val/
                                b1c9c847-3bda4659.png
                                ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    return _BDD100K_loader(path, "10k")


def _BDD100K_loader(path: str, dataset_type: str) -> Dataset:
    root_path = os.path.join(
        os.path.abspath(os.path.expanduser(path)), f"bdd100k_images_{dataset_type}"
    )
    dataset = Dataset(DATASET_NAMES[dataset_type])
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), f"catalog_{dataset_type}.json"))
    load_segment = _load_segment_10k if dataset_type == "10k" else _load_segment_100k
    labels_dir = os.path.join(root_path, "labels")
    load_segment(dataset, root_path, labels_dir)

    return dataset


def _load_segment_100k(dataset: Dataset, root_path: str, labels_dir: str) -> None:
    for segment_name in _SEGMENT_NAMES:
        segment = dataset.create_segment(segment_name)
        image_paths = glob(os.path.join(root_path, "images", "100k", segment_name, "*.jpg"))

        print(f"Reading data to segment '{segment_name}'...")
        if segment_name == "test":
            for image_path in image_paths:
                segment.append(Data(image_path))
        else:
            label_contents = _read_label_file_100k(labels_dir, segment_name)
            for image_path in image_paths:
                data = Data(image_path)
                box2d: List[LabeledBox2D] = []
                polygon: List[LabeledPolygon] = []
                polyline2d: List[LabeledPolyline2D] = []
                label = data.label
                label_content = label_contents[os.path.basename(image_path)]
                label.classification = Classification(attributes=label_content["attributes"])
                for label_info in label_content["labels"]:
                    if "box2d" in label_info:
                        _add_box2d_label(label_info, box2d)
                    if "poly2d" in label_info:
                        _add_poly2d_label_100k(label_info, polygon, polyline2d)
                label.box2d = box2d
                label.polygon = polygon
                label.polyline2d = polyline2d
                segment.append(data)
        print(f"Finished reading data to segment '{segment_name}'")


def _load_segment_10k(dataset: Dataset, root_path: str, labels_dir: str) -> None:
    for segment_name in _SEGMENT_NAMES:
        segment = dataset.create_segment(segment_name)
        image_paths = glob(os.path.join(root_path, "images", "10k", segment_name, "*.jpg"))

        print(f"Reading data to segment '{segment_name}'...")
        if segment_name == "test":
            for image_path in image_paths:
                segment.append(Data(image_path))
        else:
            single_channel_mask_dirs: Dict[str, str] = {}
            original_mask_dirs: Dict[str, str] = {}
            for seg_type, dir_names in _SEGMENTATIONS_INFO.items():
                original_mask_dirs[seg_type] = os.path.join(labels_dir, *dir_names, segment_name)
                if seg_type != "sem":
                    single_channel_mask_dir = os.path.join(
                        labels_dir,
                        "single_channel_mask",
                        segment_name,
                        dir_names[0],
                    )
                    single_channel_mask_dirs[seg_type] = single_channel_mask_dir
                    os.makedirs(single_channel_mask_dir, exist_ok=True)

            label_contents = _read_label_file_10k(labels_dir, segment_name)
            for image_path in image_paths:
                segment.append(
                    _get_data_10k(
                        image_path,
                        original_mask_dirs,
                        label_contents[os.path.basename(image_path)],
                        single_channel_mask_dirs,
                    )
                )
            print(f"Finished reading data to segment '{segment_name}'")


def _get_data_10k(
    image_path: str,
    original_mask_paths: Dict[str, str],
    label_content: Dict[str, Any],
    single_channel_mask_paths: Dict[str, str],
) -> Data:
    data = Data(image_path)
    polygon: List[LabeledPolygon] = []
    for label_info in label_content["labels"]:
        if "poly2d" in label_info:
            _add_poly2d_label_10k(label_info, polygon)
    label = data.label
    label.polygon = polygon
    stem = os.path.splitext(os.path.basename(image_path))[0]
    label.semantic_mask = SemanticMask(os.path.join(original_mask_paths["sem"], f"{stem}.png"))
    label.instance_mask = _get_instance_mask(
        stem, original_mask_paths["ins"], single_channel_mask_paths["ins"]
    )
    label.panoptic_mask = _get_panoptic_mask(
        stem, original_mask_paths["pan"], single_channel_mask_paths["pan"]
    )
    return data


def _add_box2d_label(label_info: Dict[str, Any], box2d: List[LabeledBox2D]) -> None:
    box2d_info = label_info["box2d"]
    labeled_box2d = LabeledBox2D(
        box2d_info["x1"],
        box2d_info["y1"],
        box2d_info["x2"],
        box2d_info["y2"],
        category=label_info["category"],
        attributes=label_info["attributes"],
    )
    box2d.append(labeled_box2d)


def _add_poly2d_label_100k(
    label_info: Dict[str, Any], polygon: List[LabeledPolygon], polyline2d: List[LabeledPolyline2D]
) -> None:
    poly2d_info = label_info["poly2d"][0]
    if poly2d_info["closed"]:
        labeled_polygon = LabeledPolygon(
            points=poly2d_info["vertices"],
            category=label_info["category"],
            attributes=label_info["attributes"],
        )
        polygon.append(labeled_polygon)
    else:
        labeled_polyline2d = LabeledPolyline2D(
            points=poly2d_info["vertices"],
            category=label_info["category"],
            attributes=label_info.get("attributes", {}),
            beizer_point_types=poly2d_info["types"],
        )
        polyline2d.append(labeled_polyline2d)


def _add_poly2d_label_10k(label_info: Dict[str, Any], polygon: List[LabeledPolygon]) -> None:
    poly2d_info = label_info["poly2d"][0]
    labeled_polygon = LabeledPolygon(
        points=poly2d_info["vertices"],
        category=label_info["category"],
        attributes=label_info.get("attributes", {}),
    )
    polygon.append(labeled_polygon)


def _read_label_file_100k(label_dir: str, segment_name: str) -> Dict[str, Any]:
    source_label_contents = []
    label_filenames = glob(os.path.join(label_dir, "**", f"*_{segment_name}.json"), recursive=True)

    label_prefixes = set(_LABEL_TYPE_INFO_100K)
    for label_filename in label_filenames:
        label_file_basename = os.path.basename(label_filename)
        label_prefix = label_file_basename.replace(f"_{segment_name}.json", "")
        try:
            label_prefixes.remove(label_prefix)
        except KeyError:
            warn_message = f"Invalid label file name '{label_file_basename}'! Ignoring.."
            warn(warn_message)
            continue

        label_description = _LABEL_TYPE_INFO_100K[label_prefix][0]
        print(f"Reading '{label_description}' labels to segment '{segment_name}'...")
        with open(label_filename, "r") as fp:
            source_label_contents.append(json.load(fp))
        print(f"Finished reading '{label_description}' labels to segment '{segment_name}'...")

    for missing_label_prefix in label_prefixes:
        warn_message = (
            f"Missing label file '{missing_label_prefix}_{segment_name}.json'! "
            f"The correspondent '{_LABEL_TYPE_INFO_100K[missing_label_prefix][1]}' "
            f"label will be set to empty!"
        )
        warn(warn_message)

    print(f"Merging '{segment_name}' labels...")
    label_contents = _merge_label(source_label_contents)
    print(f"Finished merging '{segment_name}' labels")
    return label_contents


def _read_label_file_10k(label_dir: str, segment_name: str) -> Dict[str, Any]:
    source_label_contents = []
    label_filename = os.path.join(label_dir, "pan_seg", "polygons", f"pan_seg_{segment_name}.json")
    with open(label_filename, "r") as fp:
        source_label_contents.append(json.load(fp))

    print(f"Merging '{segment_name}' labels...")
    label_contents = _merge_label(source_label_contents)
    print(f"Finished merging '{segment_name}' labels")
    return label_contents


def _merge_label(source_label_contents: List[List[Dict[str, Any]]]) -> Dict[str, Any]:
    label_contents: Dict[str, Any] = {}
    for source_label_content in source_label_contents:
        for image_info in source_label_content:
            image_name = image_info["name"]
            image_label = label_contents.setdefault(image_name, {})
            image_label.setdefault("labels", []).extend(image_info.get("labels", []))
            image_label.setdefault("attributes", {}).update(image_info.get("attributes", {}))

    return label_contents


def _get_instance_mask(stem: str, original_mask_dir: str, mask_dir: str) -> InstanceMask:
    mask_path = os.path.join(mask_dir, f"{stem}.png")
    mask_info = _save_and_get_mask_info(
        os.path.join(original_mask_dir, f"{stem}.png"),
        mask_path,
        os.path.join(mask_dir, f"{stem}.json"),
        "ins",
    )

    ins_mask = InstanceMask(mask_path)
    ins_mask.all_attributes = mask_info["all_attributes"]
    return ins_mask


def _get_panoptic_mask(stem: str, original_mask_dir: str, mask_dir: str) -> PanopticMask:
    mask_path = os.path.join(mask_dir, f"{stem}.png")
    mask_info = _save_and_get_mask_info(
        os.path.join(original_mask_dir, f"{stem}.png"),
        mask_path,
        os.path.join(mask_dir, f"{stem}.json"),
        "pan",
    )

    pan_mask = PanopticMask(mask_path)
    pan_mask.all_category_ids = mask_info["all_category_ids"]
    pan_mask.all_attributes = mask_info["all_attributes"]
    return pan_mask


def _save_and_get_mask_info(
    original_mask_path: str, mask_path: str, mask_info_path: str, seg_type: str
) -> Dict[str, Any]:
    if not os.path.exists(mask_path):
        mask = np.array(Image.open(original_mask_path), dtype=np.uint16)
        all_attributes = {}
        if seg_type == "pan":
            all_category_ids = {}
        for category_id, attributes, instance_id_high, instance_id_low in np.unique(
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
            if seg_type == "pan":
                all_category_ids[instance_id] = int(category_id)
        mask_info = (
            {"all_attributes": all_attributes, "all_category_ids": all_category_ids}
            if seg_type == "pan"
            else {"all_attributes": all_attributes}
        )
        with open(mask_info_path, "w") as fp:
            json.dump(mask_info, fp)
        Image.fromarray(mask[:, :, -1] + (mask[:, :, -2] << 8)).save(mask_path)
    else:
        with open(mask_info_path, "r") as fp:
            mask_info = json.load(
                fp,
                object_hook=lambda info: {
                    int(key) if key.isdigit() else key: value for key, value in info.items()
                },
            )
    return mask_info


def _BDD100K_MOTS2020(path: str) -> Dataset:
    """Load a sub-dataset MOTS2020 of BDD100K Dataset to Tensorbay.

    The dataset is named as 'BDD100K_MOTS2020'

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


def _BDD100K_MOT2020(path: str) -> Dataset:
    """Load a sub-dataset MOT2020 of BDD100K Dataset to Tensorbay.

    The dataset is named as 'BDD100K_MOT2020'

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
        os.makedirs(mask_subdir, exist_ok=True)
    with open(os.path.join(segment_labels_dir, f"{subdir_name}.json"), "r") as fp:
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
            mask_subdir,
            os.path.splitext(label_content_name)[0],
            label_content,
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
    mask_subdir: str,
    stem: str,
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
    label = data.label
    label.multi_polygon = labeled_multipolygons
    label.instance_mask = _get_instance_mask(stem, original_mask_subdir, mask_subdir)
    return data
