#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=pointless-string-statement
# pylint: disable=invalid-name
# pylint: disable=unsubscriptable-object
# flake8: noqa: F401

"""This file includes the python code of LeedsSportsPose.rst."""

"""Authorize a Client Instance"""
from tensorbay import GAS

# Please visit `https://gas.graviti.com/tensorbay/developer` to get the AccessKey.
gas = GAS("<YOUR_ACCESSKEY>")
""""""

"""Create Dataset"""
gas.create_dataset("LeedsSportsPose")
""""""

"""Organize Dataset / regular import"""
from tensorbay.dataset import Dataset

""""""

"""Organize dataset / import dataloader"""
from tensorbay.opendataset import LeedsSportsPose

dataset = LeedsSportsPose("<path/to/dataset>")
""""""

"""Upload Dataset"""
dataset_client = gas.upload_dataset(dataset, jobs=8)
dataset_client.commit("initial commit")
""""""

"""Read Dataset / get dataset"""
dataset = Dataset("LeedsSportsPose", gas)
""""""

"""Read Dataset / get segment"""
segment = dataset[0]
""""""

"""Read Dataset / get data"""
data = segment[0]
""""""

"""Read Dataset / get label"""
label_keypoints2d = data.label.keypoints2d[0]
x = data.label.keypoints2d[0][0].x
y = data.label.keypoints2d[0][0].y
v = data.label.keypoints2d[0][0].v
""""""

"""Delete Dataset"""
gas.delete_dataset("LeedsSportsPose")
""""""
