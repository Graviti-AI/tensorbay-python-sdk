#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#
# pylint: disable=invalid-name

"""This file defines the BDD100K dataloader."""

import json
import os
from glob import glob
from typing import Any, Callable, Dict, Iterable, List
from warnings import warn

from ...dataset import Data, Dataset
from ...label import (
    Classification,
    LabeledBox2D,
    LabeledMultiPolygon,
    LabeledPolygon,
    LabeledPolyline2D,
)
from ...opendataset import _utility

DATASET_NAMES = {
    "100k": "BDD100K",
    "10k": "BDD100K_10K",
    "mots": "BDD100K_MOTS2020",
    "mot": "BDD100K_MOT2020",
}
_SEGMENT_NAMES = ("train", "val")
_LABEL_TYPE_INFO = {
    "100k": {
        "det": ("Detection 2020", "BOX2D"),
        "lane": ("Lane Marking", "POLYLINE2D"),
        "drivable": ("Drivable Area", "POLYGON"),
    },
    "10k": {
        "ins_seg": ("Instance Segmentation", "POLYGON"),
        "sem_seg": ("Semantic Segmentation", "POLYLINE2D"),
        "pan_seg": ("Panoptic Segmentation", "POLYLINE2D"),
    },
}
_TRACKING_DATASET_INFO = {
    "mots": ("bdd100k_seg_track_20", "seg_track_20", os.path.join("seg_track_20", "polygons")),
    "mot": (
        "bdd100k_box_track_20",
        "",
        "",
    ),
}
_DATA_GETTER = Callable[[str, Dict[str, Any]], Data]
_DATA_GENERATOR = Callable[[str, str, _DATA_GETTER], Iterable[Data]]


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
                        test
                        train
                        val
                labels/
                    ins_seg/
                        polygons/
                            ins_seg_train.json
                            ins_seg_val.json
                    pan_seg/
                        polygons/
                            pan_seg_train.json
                            pan_seg_val.json
                    sem_seg/
                        polygons/
                            sem_seg_train.json
                            sem_seg_val.json

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

    _load_segment(dataset, root_path, dataset_type)

    return dataset


def _load_segment(dataset: Dataset, root_path: str, dataset_type: str) -> None:
    images_directory = os.path.join(root_path, "images", dataset_type)
    labels_directory = os.path.join(root_path, "labels")

    get_data = _get_data_100k if dataset_type == "100k" else _get_data_10k

    for segment_name in _SEGMENT_NAMES:
        segment = dataset.create_segment(segment_name)
        image_paths = _utility.glob(os.path.join(images_directory, segment_name, "*.jpg"))

        print(f"Reading data to segment '{segment_name}'...")
        if segment_name == "test":
            for image_path in image_paths:
                segment.append(Data(image_path))
        else:
            label_contents = _read_label_file(labels_directory, segment_name, dataset_type)
            for image_path in image_paths:
                segment.append(get_data(image_path, label_contents[os.path.basename(image_path)]))
        print(f"Finished reading data to segment '{segment_name}'")


def _get_data_10k(image_path: str, label_content: Dict[str, Any]) -> Data:
    data = Data(image_path)
    polygon: List[LabeledPolygon] = []
    polyline2d: List[LabeledPolyline2D] = []
    for label_info in label_content["labels"]:
        if "poly2d" in label_info:
            _add_poly2d_label(label_info, polygon, polyline2d)
    data.label.polygon = polygon
    data.label.polyline2d = polyline2d
    return data


def _get_data_100k(image_path: str, label_content: Dict[str, Any]) -> Data:
    data = Data(image_path)
    box2d: List[LabeledBox2D] = []
    polygon: List[LabeledPolygon] = []
    polyline2d: List[LabeledPolyline2D] = []
    data.label.classification = Classification(attributes=label_content["attributes"])
    for label_info in label_content["labels"]:
        if "box2d" in label_info:
            _add_box2d_label(label_info, box2d)
        if "poly2d" in label_info:
            _add_poly2d_label(label_info, polygon, polyline2d)
    data.label.box2d = box2d
    data.label.polygon = polygon
    data.label.polyline2d = polyline2d
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


def _add_poly2d_label(
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
        )
        polyline2d.append(labeled_polyline2d)


def _read_label_file(label_directory: str, segment_name: str, dataset_type: str) -> Dict[str, Any]:
    source_label_contents = []
    label_filenames = glob(
        os.path.join(label_directory, "**", f"*_{segment_name}.json"), recursive=True
    )

    label_type_info = _LABEL_TYPE_INFO[dataset_type]
    label_prefixes = set(label_type_info)
    for label_filename in label_filenames:
        label_file_basename = os.path.basename(label_filename)
        label_prefix = label_file_basename.replace(f"_{segment_name}.json", "")
        try:
            label_prefixes.remove(label_prefix)
        except KeyError:
            warn_message = f"Invalid label file name '{label_file_basename}'! Ignoring.."
            warn(warn_message)
            continue

        label_description = label_type_info[label_prefix][0]
        print(f"Reading '{label_description}' labels to segment '{segment_name}'...")
        with open(label_filename, "r") as fp:
            source_label_contents.append(json.load(fp))
        print(f"Finished reading '{label_description}' labels to segment '{segment_name}'...")

    for missing_label_prefix in label_prefixes:
        warn_message = (
            f"Missing label file '{missing_label_prefix}_{segment_name}.json'! "
            f"The correspondent '{label_type_info[missing_label_prefix][1]}' "
            f"label will be set to empty!"
        )
        warn(warn_message)

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
    if tracking_type == "mot":
        get_data = _get_mot_data
    else:
        get_data = _get_mots_data
    root_path = os.path.join(
        os.path.abspath(os.path.expanduser(path)), _TRACKING_DATASET_INFO[tracking_type][0]
    )
    dataset = Dataset(DATASET_NAMES[tracking_type])
    dataset.notes.is_continuous = True
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), f"catalog_{tracking_type}.json"))
    images_directory = os.path.join(root_path, "images", _TRACKING_DATASET_INFO[tracking_type][1])
    labels_directory = os.path.join(root_path, "labels", _TRACKING_DATASET_INFO[tracking_type][2])
    _load_tracking_segment(dataset, images_directory, labels_directory, get_data)

    return dataset


def _load_tracking_segment(
    dataset: Dataset,
    images_directory: str,
    labels_directory: str,
    load_label: _DATA_GETTER,
) -> None:
    for segment_prefix in _SEGMENT_NAMES:
        image_directory = _utility.glob(os.path.join(images_directory, segment_prefix, "*"))
        labels_directory_segment = os.path.join(labels_directory, segment_prefix)
        if segment_prefix == "test":
            generate_data: _DATA_GENERATOR = _generate_test_data
        else:
            generate_data = _generate_data
        for image_subdir in image_directory:
            segment = dataset.create_segment(f"{segment_prefix}_{os.path.basename(image_subdir)}")
            segment.extend(generate_data(image_subdir, labels_directory_segment, load_label))


def _generate_test_data(image_subdir: str, _: str, __: _DATA_GETTER) -> Iterable[Data]:
    yield from map(Data, _utility.glob(os.path.join(image_subdir, "*.jpg")))


def _generate_data(
    image_subdir: str,
    labels_directory_segment: str,
    get_data: _DATA_GETTER,
) -> Iterable[Data]:
    label_filename = f"{os.path.basename(image_subdir)}.json"
    with open(os.path.join(labels_directory_segment, label_filename), "r") as fp:
        label_contents = json.load(fp)
    for label_content in label_contents:
        label_content_name = label_content["name"]
        if "/" in label_content_name:
            label_content_name = label_content_name[len(label_content["videoName"]) + 1 :]
        image_path = os.path.join(image_subdir, label_content_name)

        yield get_data(image_path, label_content)


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


def _get_mots_data(image_path: str, label_content: Dict[str, Any]) -> Data:
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
    data.label.multi_polygon = labeled_multipolygons

    return data
