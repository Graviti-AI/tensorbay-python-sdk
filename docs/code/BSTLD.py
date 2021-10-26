#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=pointless-string-statement
# pylint: disable=invalid-name
# pylint: disable=unsubscriptable-object
# flake8: noqa: F401

"""This file includes the python code of BSTLD.rst and read_dataset_class.rst."""

"""Authorize a Client Instance"""
from tensorbay import GAS

ACCESS_KEY = "Accesskey-*****"
gas = GAS(ACCESS_KEY)
""""""

"""Create Dataset"""
gas.create_dataset("BSTLD")
""""""

"""Organize Dataset / regular import"""
from tensorbay.dataset import Dataset

""""""

"""Organize dataset / import dataloader"""
from tensorbay.opendataset import BSTLD

dataset = BSTLD("path/to/dataset/directory")
""""""

"""Upload Dataset"""
dataset_client = gas.upload_dataset(dataset, jobs=8, skip_uploaded_files=True)
dataset_client.commit("initial commit")
""""""

"""Read Dataset / get dataset"""
dataset = Dataset("BSTLD", gas)
""""""

"""Read Dataset / list segment names"""
dataset.keys()
""""""

"""Read Dataset / get segment"""
first_segment = dataset[0]
train_segment = dataset["train"]
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
