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

"""This file includes the python code of BSTLD.rst and read_dataset_class.rst."""

"""Authorize a Client Object"""
from tensorbay import GAS

ACCESS_KEY = "Accesskey-*****"
gas = GAS(ACCESS_KEY)
""""""

"""Create Dataset"""
gas.create_dataset("BSTLD")
""""""

"""List Dataset Names"""
list(gas.list_dataset_names())
""""""

"""Read Dataset Class / organize dataset"""
from tensorbay.opendataset import BSTLD

dataset = BSTLD("path/to/dataset/directory")
""""""

"""Upload Dataset"""
# dataset is the one you initialized in "Organize Dataset" section
dataset_client = gas.upload_dataset(dataset, jobs=8, skip_uploaded_files=False)
dataset_client.commit("BSTLD")
""""""

"""Read Dataset / get dataset"""
dataset_client = gas.get_dataset("BSTLD")
""""""

"""Read Dataset / list segment names"""
list(dataset_client.list_segment_names())
""""""

"""Read Dataset Class / get a segment"""
train_segment = dataset.get_segment_by_name("train")
first_segment = dataset[0]
""""""

"""Read Dataset / get segment"""
from tensorbay.dataset import Segment

train_segment = Segment("train", dataset_client)
""""""

"""Read Dataset / get data"""
data = train_segment[3]
""""""

"""Read Dataset / get label"""
label_box2d = data.label.box2d[0]
category = label_box2d.category
attributes = label_box2d.attributes
""""""

"""Delete Dataset"""
gas.delete_dataset("BSTLD")
""""""
