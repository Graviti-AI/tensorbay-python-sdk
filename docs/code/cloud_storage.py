#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=pointless-string-statement

"""This file includes the python code of auth cloud storage import."""

"""Get cloud client"""
from tensorbay import GAS

gas = GAS("Accesskey-*****")
cloud_client = gas.get_cloud_client("config_name")
""""""

"""Import dataset from cloud platform to the authorized storage dataset"""
import json

from tensorbay.dataset import Dataset
from tensorbay.label import Classification

# Use AuthData to organize a dataset by the "Dataset" class before importing.
dataset = Dataset("DatasetName")

# TensorBay uses "segment" to separate different parts in a dataset.
segment = dataset.create_segment()

images = cloud_client.list_auth_data("data/images")
labels = cloud_client.list_auth_data("data/labels")

for auth_data, label in zip(images, labels):
    with label.open() as fp:
        auth_data.label.classification = Classification.loads(json.load(fp))
    segment.append(auth_data)

dataset_client = gas.upload_dataset(dataset, jobs=8)
""""""
