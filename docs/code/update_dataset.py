#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=pointless-string-statement
# pylint: disable=wrong-import-position
# pylint: disable=invalid-name
# type: ignore[arg-type]

"""Authorize a Client Instance."""
from tensorbay import GAS

"""Upload Images to the Dataset"""
from tensorbay.dataset import Dataset

dataset = Dataset("DatasetName")
ACCESS_KEY = "Accesskey-*****"
gas = GAS(ACCESS_KEY)
""""""

"""Update dataset meta"""
gas.update_dataset("DATASET_NAME", alias="alias", is_public=True)
""""""

"""Update dataset notes"""
dataset_client = gas.get_dataset("DATASET_NAME")
dataset_client.create_draft("draft-1")
dataset_client.update_notes(is_continuous=True)
dataset_client.commit("update notes")
""""""

"""Update label / get dataset an create draft"""
dataset_client.create_draft("draft-2")
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

"""Update data/ upload dataset"""
gas.upload_dataset(dataset, jobs=8, skip_uploaded_files=True)
""""""

"""Update data/ overwrite dataset"""
gas.upload_dataset(dataset, jobs=8)
""""""

"""Update data/ delete segment"""
dataset_client.create_draft("draft-3")
dataset_client.delete_segment("SegmentName")
""""""

"""Update data/ delete data"""
segment_client = dataset_client.get_segment("SegmentName")
segment_client.delete_data("a.png")
""""""

"""Delete frame"""
segment_client.delete_frame("00000000003W09TEMC1HXYMC74")
""""""
