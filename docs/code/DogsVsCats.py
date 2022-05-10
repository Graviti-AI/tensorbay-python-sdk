#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=pointless-string-statement
# pylint: disable=invalid-name
# pylint: disable=unsubscriptable-object
# flake8: noqa: F401

"""This files includes the python code example in dogsvscats.rst."""

"""Authorize a Client Instance"""
from tensorbay import GAS

# Please visit `https://gas.graviti.com/tensorbay/developer` to get the AccessKey.
gas = GAS("<YOUR_ACCESSKEY>")
""""""

"""Create Dataset"""
gas.create_dataset("DogsVsCats")
""""""

"""Organize Dataset / regular import"""
from tensorbay.dataset import Dataset

""""""

"""Organize dataset / import dataloader"""
from tensorbay.opendataset import DogsVsCats

dataset = DogsVsCats("<path/to/dataset>")
""""""

"""Upload Dataset"""
dataset_client = gas.upload_dataset(dataset, jobs=8)
dataset_client.commit("initial commit")
""""""

"""Read Dataset / get dataset"""
dataset = Dataset("DogsVsCats", gas)
""""""

"""Read Dataset / list segment names"""
dataset.keys()
""""""

"""Read Dataset / get segment"""
segment = dataset["train"]
""""""

"""Read Dataset / get data"""
data = segment[0]
""""""

"""Read Dataset / get label"""
category = data.label.classification.category
""""""

"""Delete Dataset"""
gas.delete_dataset("DogsVsCats")
""""""
