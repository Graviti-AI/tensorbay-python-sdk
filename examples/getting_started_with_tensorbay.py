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

"""Authorize a Client Instance"""
from tensorbay import GAS

gas = GAS("<YOUR_ACCESSKEY>")
""""""

"""Create a Dataset"""
gas.create_dataset("DatasetName")
""""""

"""List Dataset Names"""
dataset_names = gas.list_dataset_names()
""""""

"""Upload Images to the Dataset"""
from tensorbay.dataset import Data, Dataset

# Organize the local dataset by the "Dataset" class before uploading.
dataset = Dataset("DatasetName")

# TensorBay uses "segment" to separate different parts in a dataset.
segment = dataset.create_segment()

segment.append(Data("0000001.jpg"))
segment.append(Data("0000002.jpg"))

dataset_client = gas.upload_dataset(dataset)

# TensorBay provides dataset version control feature, commit the uploaded data before using it.
dataset_client.commit("Initial commit")
""""""

"""Read Images from the Dataset"""
from PIL import Image

dataset = Dataset("DatasetName", gas)
segment = dataset[0]

for data in segment:
    with data.open() as fp:
        image = Image.open(fp)
        width, height = image.size
        image.show()
""""""

"""Delete the Dataset"""
gas.delete_dataset("DatasetName")
""""""
