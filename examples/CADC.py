#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=not-callable
# pylint: disable=ungrouped-imports
# pylint: disable=import-error
# pylint: disable=pointless-string-statement
# pylint: disable=invalid-name

"""This file includes the python code of CADC.rst."""

"""Authorize a Client Object"""
from tensorbay import GAS

ACCESS_KEY = "Accesskey-*****"
gas = GAS(ACCESS_KEY)
""""""

"""Create Fusion Dataset"""
gas.create_dataset("CADC", is_fusion=True)
""""""

"""List Dataset Names"""
list(gas.list_dataset_names())
""""""

from tensorbay.opendataset import CADC

fusion_dataset = CADC("path/to/dataset/directory")

"""Upload Fusion Dataset"""
# fusion_dataset is the one you initialized in "Organize Fusion Dataset" section
fusion_dataset_client = gas.upload_dataset(fusion_dataset, jobs=8, skip_uploaded_files=False)
fusion_dataset_client.commit("CADC")
""""""

"""Read Fusion Dataset / get fusion dataset"""
fusion_dataset_client = gas.get_dataset("CADC", is_fusion=True)
""""""

"""Read Dataset / list fusion segment names"""
list(fusion_dataset_client.list_segment_names())
""""""

"""Read Fusion Dataset / get fusion segment"""
from tensorbay.dataset import FusionSegment

fusion_segment = FusionSegment("2018_03_06/0001", fusion_dataset_client)
""""""

"""Read Fusion Dataset / get sensors"""
sensors = fusion_segment.sensors
""""""

"""Read Fusion Dataset / get frame"""
frame = fusion_segment[0]
""""""

"""Read Fusion Dataset / get data"""
for sensor_name in sensors:
    data = frame[sensor_name]
""""""

"""Read Fusion Dataset / get label"""
lidar_data = frame["LIDAR"]
label_box3d = lidar_data.label.box3d[0]
category = label_box3d.category
attributes = label_box3d.attributes
""""""

"""Delete Fusion Dataset"""
gas.delete_dataset("CADC")
""""""
