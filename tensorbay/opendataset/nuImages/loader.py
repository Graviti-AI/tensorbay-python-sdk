#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of nuImages dataset."""

import base64
import os
from typing import Any, Dict, Iterator, List, Optional, Tuple

from tensorbay.dataset import Data, Frame, FusionDataset, FusionSegment
from tensorbay.label import LabeledBox2D, LabeledRLE
from tensorbay.opendataset._utility.nuScenes import (
    get_info_with_determined_token,
    get_info_with_token,
    get_sensor,
    transpose_rle,
    uncompress_rle,
)

DATASET_NAME = "nuImages"


def nuImages(path: str) -> FusionDataset:
    """`nuImages <https://www.nuscenes.org/nuimages>`_ dataset.

    The file structure should be like::

        <path>
            nuimages-v1.0-all-metadata/
                v1.0-mini/
                    attribute.json
                    calibrated_sensor.json
                    category.json
                    ego_pose.json
                    instance.json
                    log.json
                    object_ann.json
                    sample_data.json
                    sample.json
                    sensor.json
                    surface_ann.json
                v1.0-test/
                    ...
                v1.0-train/
                    ...
                v1.0-val/
                    ...
            samples/
                CAM_BACK/
                CAM_BACK_LEFT/
                CAM_BACK_RIGHT/
                CAM_FRONT/
                CAM_FRONT_LEFT/
                CAM_FRONT_RIGHT/
            sweeps/
                CAM_BACK/
                CAM_BACK_LEFT/
                CAM_BACK_RIGHT/
                CAM_FRONT/
                CAM_FRONT_LEFT/
                CAM_FRONT_RIGHT/
            nuimages-v1.0-mini/
                samples/
                    ...
                sweeps/
                    ...
                v1.0-mini/
                   ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = FusionDataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    metadata_path = os.path.join(root_path, "nuimages-v1.0-all-metadata")
    for subset in os.listdir(metadata_path):
        dataset.add_segment(_get_segment(root_path, subset, metadata_path))
    return dataset


def _get_segment(root_path: str, subset: str, metadata_path: str) -> FusionSegment:
    is_test = subset.endswith("test")
    annotation_info = _get_annotation_info(os.path.join(metadata_path, subset), is_test)
    segment = FusionSegment(subset)
    _load_frame_and_sensor(segment, annotation_info, root_path, is_test)
    return segment


def _get_annotation_info(info_path: str, is_test: bool = False) -> Dict[str, Any]:
    annotation_info = {
        "samples": get_info_with_token(info_path, "sample"),
        "frame_data": get_info_with_determined_token(info_path, "sample_data"),
        "calibrated_sensors": get_info_with_token(info_path, "calibrated_sensor"),
        "ego_poses": get_info_with_token(info_path, "ego_pose"),
        "sensor": get_info_with_token(info_path, "sensor"),
    }
    if not is_test:
        annotation_info["object_annotations"] = get_info_with_determined_token(
            info_path, "object_ann", no_key_frame=True, determined_token="sample_data_token"
        )
        annotation_info["surface_annotations"] = get_info_with_determined_token(
            info_path, "surface_ann", no_key_frame=True, determined_token="sample_data_token"
        )
        annotation_info["category"] = get_info_with_token(info_path, "category")
        annotation_info["attribute"] = get_info_with_token(info_path, "attribute")
    return annotation_info


def _load_frame_and_sensor(
    segment: FusionSegment,
    annotation_info: Dict[str, Any],
    subset_path: str,
    is_test: bool,
) -> None:
    frame = Frame()
    for data_frames in annotation_info["frame_data"].values():
        for data_frame in data_frames:
            calibrated_sensor_info = annotation_info["calibrated_sensors"][
                data_frame["calibrated_sensor_token"]
            ]
            common_sensor = annotation_info["sensor"][calibrated_sensor_info["sensor_token"]]
            sensor_name = common_sensor["channel"]

            if sensor_name not in segment.sensors:
                segment.sensors.add(get_sensor("camera", sensor_name, calibrated_sensor_info))

            data = Data(
                os.path.join(subset_path, data_frame["filename"]),
                timestamp=data_frame["timestamp"] / 10 ** 6,
            )

            if not is_test:
                data.label.box2d, data.label.rle = _get_labels(data_frame["token"], annotation_info)

            frame[sensor_name] = data
        segment.append(frame)


def _get_labels(
    sample_data_token: str,
    annotation_info: Dict[str, Dict[str, Any]],
) -> Tuple[List[LabeledBox2D], List[LabeledRLE]]:
    object_annotations = annotation_info["object_annotations"]
    surface_annotations = annotation_info["surface_annotations"]
    categories = annotation_info["category"]
    attributes = annotation_info["attribute"]
    label_box2d: List[LabeledBox2D] = []
    label_rle: List[LabeledRLE] = []
    if sample_data_token in object_annotations:
        for box2d, rle in _get_object_annotations(
            object_annotations[sample_data_token], categories, attributes
        ):
            label_box2d.append(box2d)
            if rle:
                label_rle.append(rle)
    if sample_data_token in surface_annotations:
        for rle in _get_surface_annotations(surface_annotations[sample_data_token], categories):
            label_rle.append(rle)
    return label_box2d, label_rle


def _get_object_annotations(
    object_annotations: List[Dict[str, Any]],
    token_to_categories: Dict[str, Any],
    token_to_attributes: Dict[str, Any],
) -> Iterator[Tuple[LabeledBox2D, Optional[LabeledRLE]]]:
    for object_annotation in object_annotations:
        category = token_to_categories[object_annotation["category_token"]]["name"]
        attributes = {}
        for attribute_token in object_annotation["attribute_tokens"]:
            key, value = token_to_attributes[attribute_token]["name"].rsplit(".", 1)
            attributes[key] = value
        box2d = LabeledBox2D(*object_annotation["bbox"], category=category, attributes=attributes)
        mask = object_annotation["mask"]
        rle = _get_labeled_rle(mask, category, attributes) if mask else None
        yield box2d, rle


def _get_surface_annotations(
    surface_annotations: List[Dict[str, Any]], categories: Dict[str, Any]
) -> Iterator[LabeledRLE]:
    for surface_annotation in surface_annotations:
        mask = surface_annotation["mask"]
        yield _get_labeled_rle(mask, categories[surface_annotation["category_token"]]["name"])


def _get_labeled_rle(
    mask: Dict[str, str],
    category: Optional[str] = None,
    attributes: Optional[Dict[str, str]] = None,
) -> LabeledRLE:
    return LabeledRLE(
        transpose_rle(
            uncompress_rle(bytes.decode(base64.b64decode(mask["counts"]))), *mask["size"]
        ),
        category=category,
        attributes=attributes,
    )
