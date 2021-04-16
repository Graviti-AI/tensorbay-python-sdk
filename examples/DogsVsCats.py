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

"""This files includes the python code example in dogsvscats.rst."""

"""Authorize a Client Instance"""
from tensorbay import GAS

ACCESS_KEY = "Accesskey-*****"
gas = GAS(ACCESS_KEY)
""""""

"""Create Dataset"""
gas.create_dataset("DogsVsCats")
""""""

"""List Dataset Names"""
gas.list_dataset_names()
""""""

from tensorbay.opendataset import DogsVsCats

dataset = DogsVsCats("path/to/dataset/directory")

"""Upload Dataset"""
# dataset is the one you initialized in "Organize Dataset" section
dataset_client = gas.upload_dataset(dataset, jobs=8, skip_uploaded_files=False)
dataset_client.commit("initial commit")
""""""

"""Read Dataset / get dataset"""
dataset_client = gas.get_dataset("DogsVsCats")
""""""

"""Read Dataset / list segment names"""
dataset_client.list_segment_names()
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
data = train_segment[0]
""""""

"""Read Dataset / get label"""
category = data.label.classification.category
""""""

"""Delete Dataset"""
gas.delete_dataset("DogsVsCats")
""""""
