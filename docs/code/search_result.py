#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=pointless-string-statement
# pylint: disable=pointless-statement
# pylint: disable=invalid-name
# type: ignore[attr-defined]
# https://github.com/python/mypy/issues/5858

"""This file includes the python code of search_result.rst."""

"""Obtain a SearchResult Instance"""
from tensorbay import GAS

# Please visit `https://gas.graviti.cn/tensorbay/developer` to get the AccessKey.
gas = GAS("<YOUR_ACCESSKEY>")
dataset_client = gas.get_dataset("<DATASET_NAME>")

job = dataset_client.basic_search.create_job(
    title="search example",
    description="search description",
    conjunction="AND",
    unit="FILE",
    filters=[
        (
            "category",
            "in",
            [
                "human.pedestrian.adult",
                "human.pedestrian.child",
                "human.pedestrian.construction_worker",
            ],
            "BOX3D",
        ),
        ("size", ">", 0),
        ("withLabel", "=", True),
        ("attribute", "in", {"attribute_1": [True, False], "attribute_2": [1, 2]}, "BOX3D"),
    ],
)
search_result = job.result
""""""

"""Create Dataset"""
search_result.create_dataset("<DATASET_NAME>")
""""""

"""Get Label Statistics"""
search_result.get_label_statistics()
""""""

"""List Segment names"""
search_result.list_segment_names()
""""""

"""List Data"""
search_result.list_data(segment_name="<SEGMENT_NAME>")
""""""

"""Obtain a FusionSearchResult Instance"""
fusion_dataset_client = gas.get_dataset("<DATASET_NAME>", is_fusion=True)

job = dataset_client.basic_search.create_job(
    title="search example",
    description="search description",
    conjunction="AND",
    unit="Frame",
    filters=[
        ("sensor", "in", ["CAM_BACK_RIGHT", "CAM_FRONT"]),
        ("size", ">", 0),
        ("withLabel", "=", True),
        ("attribute", "in", {"attribute_1": [True, False], "attribute_2": [1, 2]}, "BOX3D"),
    ],
)
fusion_search_result = job.result
""""""

"""The same function as SearchResult"""
fusion_search_result.create_dataset("<DATASET_NAME>")

fusion_search_result.get_label_statistics()

fusion_search_result.list_segment_names()
""""""

"""List Frames"""
fusion_search_result.list_frames(segment_name="<SEGMENT_NAME>")
""""""

"""Get Sensors"""
fusion_search_result.get_sensors(segment_name="<SEGMENT_NAME>")
""""""
