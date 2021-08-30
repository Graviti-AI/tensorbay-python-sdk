#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=ungrouped-imports
# pylint: disable=pointless-string-statement


"""This file includes the python code of merged_dataset.rst."""

"""Create Target Dataset"""
from tensorbay import GAS

ACCESS_KEY = "Accesskey-*****"
gas = GAS(ACCESS_KEY)
dataset_client = gas.create_dataset("mergedDataset")
dataset_client.create_draft("merge dataset")
""""""

"""Copy Segment From Pet"""
pet_dataset_client = gas.get_dataset("OxfordIIITPet")
dataset_client.copy_segment("train", target_name="trainval", source_client=pet_dataset_client)
dataset_client.copy_segment("test", source_client=pet_dataset_client)
""""""

"""Upload Catalog"""
dataset_client.upload_catalog(pet_dataset_client.get_catalog())
""""""

"""Unify Category"""
from tensorbay.dataset import Data

segment_client = dataset_client.get_segment("train")
for remote_data in segment_client.list_data():
    data = Data(remote_data.path)
    data.label = remote_data.label
    data.label.classification.category = data.label.classification.category.split(".")[0]
    segment_client.upload_label(data)
""""""

"""Copy Data From Dog VS Cat"""
pet_dataset_client = gas.get_dataset("DogsVsCats")
for name in ["test", "train"]:
    source_segment_client = pet_dataset_client.get_segment(name)
    segment_client = dataset_client.get_segment(name)
    segment_client.copy_data(
        source_segment_client.list_data_paths(), source_client=source_segment_client
    )
""""""
