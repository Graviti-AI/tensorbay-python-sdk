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

"""This file includes the python code of getting_started_with_tensorbay.rst."""

"""Authorize a Client Object"""
from tensorbay import GAS

gas = GAS("<YOUR_ACCESSKEY>")
""""""

"""Create a Dataset"""
gas.create_dataset("DatasetName")
""""""

"""List Dataset Names"""
dataset_list = list(gas.list_dataset_names())
""""""

"""Upload Images to the Dataset"""
from tensorbay.dataset import Data, Dataset

# Organize the local dataset by the "Dataset" class before uploading.
dataset = Dataset("DatasetName")

# TensorBay uses "segment" to separate different parts in a dataset.
segment = dataset.create_segment()

segment.append(Data("0000001.jpg"))
segment.append(Data("0000002.jpg"))

gas.upload_dataset(dataset)
""""""

"""Read Images from the Dataset"""
from PIL import Image
from tensorbay.dataset import Segment

dataset_client = gas.get_dataset("DatasetName")

segment = Segment("", dataset_client)

for data in segment:
    with data.open() as fp:
        image = Image(fp)
        width, height = image.size
        image.show()
""""""

"""Delete the Dataset"""
gas.delete_dataset("DatasetName")
""""""
