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

"""This file includes the python code of NeolixOD.rst."""

"""Authorize a Client Object"""
from tensorbay import GAS

ACCESS_KEY = "Accesskey-*****"
gas = GAS(ACCESS_KEY)
""""""

"""Create Dataset"""
gas.create_dataset("Neolix OD")
""""""

"""List Dataset Names"""
list(gas.list_dataset_names())
""""""

from tensorbay.opendataset import NeolixOD

dataset = NeolixOD("path/to/dataset/directory")

"""Upload Dataset"""
# dataset is the one you initialized in "Organize Dataset" section
dataset_client = gas.upload_dataset(dataset, jobs=8, skip_uploaded_files=False)
dataset_client.commit("Neolix OD")
""""""

"""Read Dataset / get dataset"""
dataset_client = gas.get_dataset("Neolix OD")
""""""

"""Read Dataset / get segment"""
from tensorbay.dataset import Segment

default_segment = Segment("", dataset_client)
""""""

"""Read Dataset / get data"""
data = default_segment[0]
""""""

"""Read Dataset / get label"""
label_box3d = data.label.box3d[0]
category = label_box3d.category
attributes = label_box3d.attributes
""""""

"""Delete Dataset"""
gas.delete_dataset("Neolix OD")
""""""
