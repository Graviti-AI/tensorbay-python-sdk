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

"""This files includes the python code example in dogsvscats.rst."""

"""Authorize a Client Instance"""
from tensorbay import GAS

ACCESS_KEY = "Accesskey-*****"
gas = GAS(ACCESS_KEY)
""""""

"""Create Dataset"""
gas.create_dataset("DogsVsCats")
""""""

"""Organize Dataset / regular import"""
from tensorbay.dataset import Data, Dataset
from tensorbay.label import Classification

""""""

"""Organize dataset / import dataloader"""
from tensorbay.opendataset import DogsVsCats

dataset = DogsVsCats("path/to/dataset/directory")
""""""

"""Upload Dataset"""
dataset_client = gas.upload_dataset(dataset)
dataset_client.commit("initial commit")
""""""

"""Read Dataset / get dataset"""
dataset_client = gas.get_dataset("DogsVsCats")
""""""

"""Read Dataset / list segment names"""
dataset_client.list_segment_names()
""""""

"""Read Dataset Class / get a segment"""
train_segment = dataset["train"]
first_segment = dataset[0]
""""""

"""Read Dataset / get segment"""
from tensorbay.dataset import Segment

train_segment = Segment("train", dataset_client)
""""""

"""Read Dataset / get data"""
data = train_segment[0]
""""""

"""Read Dataset / get label"""
category = data.label.classification.category
""""""

"""Delete Dataset"""
gas.delete_dataset("DogsVsCats")
""""""
