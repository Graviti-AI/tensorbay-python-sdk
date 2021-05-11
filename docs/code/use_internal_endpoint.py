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

"""This file includes the python code of use_internal_network."""


"""Usage of Upload Dataset By Internal Endpoint"""
from tensorbay import GAS
from tensorbay.client import config
from tensorbay.dataset import Data, Dataset

# Set is_internal to True for using internal endpoint.
config.is_internal = True

gas = GAS("<YOUR_ACCESSKEY>")

# Organize the local dataset by the "Dataset" class before uploading.
dataset = Dataset("DatasetName")

segment = dataset.create_segment()
segment.append(Data("0000001.jpg"))
segment.append(Data("0000002.jpg"))

# All the data will be uploaded through internal endpoint.
dataset_client = gas.upload_dataset(dataset)

dataset_client.commit("Initial commit")
""""""
