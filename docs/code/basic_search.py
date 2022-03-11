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

"""This file includes the python code of basic_search.rst."""

"""Authorize a Dataset Client Instance"""
from tensorbay import GAS

# Please visit `https://gas.graviti.cn/tensorbay/developer` to get the AccessKey.
gas = GAS("<YOUR_ACCESSKEY>")
dataset_client = gas.create_dataset("<DATASET_NAME>")

""""""

"""Create Job"""
dataset_client.basic_search.create_job(
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
""""""

"""Get and List"""
job = dataset_client.basic_search.get_job("<JOB_ID>")
job = dataset_client.basic_search.list_jobs()[0]
""""""

"""Get Job Info"""
job.status
job.result
job.error_message
job.arguments
""""""

"""Update Job"""
job.update()
job.update(until_complete=True)
""""""

"""Abort and Retry Job"""
job.abort()
job.retry()
""""""
