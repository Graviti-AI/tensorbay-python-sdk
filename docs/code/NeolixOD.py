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
# pylint: disable=unused-import
# flake8: noqa: F401

"""This file includes the python code of NeolixOD.rst."""

"""Authorize a Client Instance"""
from tensorbay import GAS

ACCESS_KEY = "Accesskey-*****"
gas = GAS(ACCESS_KEY)
""""""

"""Create Dataset"""
gas.create_dataset("NeolixOD")
""""""

"""Organize Dataset / regular import"""
from tensorbay.dataset import Data, Dataset
from tensorbay.label import LabeledBox3D

""""""

"""Organize dataset / import dataloader"""
from tensorbay.opendataset import NeolixOD

dataset = NeolixOD("path/to/dataset/directory")
""""""

"""Upload Dataset"""
dataset_client = gas.upload_dataset(dataset, jobs=8)
dataset_client.commit("initial commit")
""""""

"""Read Dataset / get dataset"""
dataset = Dataset("NeolixOD", gas)
""""""

"""Read Dataset / get segment"""
segment = dataset[0]
""""""

"""Read Dataset / get data"""
data = segment[0]
""""""

"""Read Dataset / get label"""
label_box3d = data.label.box3d[0]
category = label_box3d.category
attributes = label_box3d.attributes
""""""

"""Delete Dataset"""
gas.delete_dataset("NeolixOD")
""""""
