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
# type: ignore[attr-defined]

"""This file includes the python code of VOC2012Segmentation.rst."""

"""Authorize a Client Instance"""
from tensorbay import GAS

# Please visit `https://gas.graviti.com/tensorbay/developer` to get the AccessKey.
gas = GAS("<YOUR_ACCESSKEY>")
""""""

"""Create Dataset"""
gas.create_dataset("VOC2012Segmentation")
""""""

"""Organize Dataset / regular import"""
from tensorbay.dataset import Dataset

""""""

"""Organize dataset / import dataloader"""
from tensorbay.opendataset import VOC2012Segmentation

dataset = VOC2012Segmentation("<path/to/dataset>")
""""""

"""Upload Dataset"""
dataset_client = gas.upload_dataset(dataset, jobs=8)
dataset_client.commit("initial commit")
""""""

"""Read Dataset / get dataset"""
dataset = Dataset("VOC2012Segmentation", gas)
""""""

"""Read Dataset / get segment"""
segment_names = dataset.keys()
segment = dataset[0]
""""""

"""Read Dataset / get data"""
data = segment[0]
""""""

"""Read Dataset / get label"""
from PIL import Image

label_semantic_mask = data.label.semantic_mask
semantic_all_attributes = label_semantic_mask.all_attributes
semantic_mask = Image.open(label_semantic_mask.open())
semantic_mask.show()

label_instance_mask = data.label.instance_mask
instance_all_attributes = label_instance_mask.all_attributes
instance_mask_url = label_instance_mask.get_url()
""""""

"""Delete Dataset"""
gas.delete_dataset("VOC2012Segmentation")
""""""
