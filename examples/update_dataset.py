#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=pointless-string-statement
# pylint: disable=wrong-import-position
# type: ignore[arg-type]

"""Authorize a Client Instance."""
from tensorbay import GAS

"""Upload Images to the Dataset"""
from tensorbay.dataset import Dataset

dataset = Dataset("DatasetName")
ACCESS_KEY = "Accesskey-*****"
gas = GAS(ACCESS_KEY)
""""""

"""Update label / get dataset an create draft"""
dataset_client = gas.get_dataset("DATASET_NAME")
dataset_client.create_draft("draft-1")
""""""

"""Update label / update catalog"""
dataset_client.upload_catalog(dataset.catalog)
""""""

"""Update label / overwrite label"""
for segment in dataset:
    segment_client = dataset_client.get_segment(segment.name)
    for data in segment:
        segment_client.upload_label(data)
""""""

"""Update label / commit dataset"""
dataset_client.commit("update labels")
""""""

"""Updata data/ upload dataset"""
gas.upload_dataset(dataset, skip_uploaded_files=True)
""""""

"""Updata data/ overwrite dataset"""
gas.upload_dataset(dataset)
""""""

"""Updata data/ delete segment"""
dataset_client.delete_segment("SegmentName")
""""""

"""Updata data/ delete data"""
segment_client = dataset_client.get_segment("SegmentName")
segment_client.delete_data(["a.png", "b.png"])
""""""
