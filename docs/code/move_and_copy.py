#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=ungrouped-imports
# pylint: disable=pointless-statement
# pylint: disable=pointless-string-statement
# pylint: disable=invalid-name
# pylint: disable=invalid-sequence-index


"""This file includes the python code of move_and_copy.rst."""

"""Get Dataset Client"""
from tensorbay import GAS

ACCESS_KEY = "Accesskey-*****"
gas = GAS(ACCESS_KEY)
dataset_client = gas.get_dataset("OxfordIIITPet")
dataset_client.list_segment_names()
# test, trainval
""""""

"""Copy Segment"""
dataset_client.create_draft("draft-1")
segment_client = dataset_client.copy_segment("test", "test_1")
segment_client.name
# test_1
dataset_client.list_segment_names()
# test, test_1, trainval
dataset_client.commit("copy test segment to test_1 segment")
""""""

"""Move Segment"""
dataset_client.create_draft("draft-2")
segment_client = dataset_client.move_segment("test", "test_2")
segment_client.name
# test_2
dataset_client.list_segment_names()
# test_1, trainval, test_2
dataset_client.commit("move test segment to test_2 segment")
""""""

"""Copy Data"""
dataset_client.create_draft("draft-3")
target_segment_client = dataset_client.create_segment("abyssinian")
for name in ["test_1", "trainval"]:
    segment_client = dataset_client.get_segment(name)
    for file_name in segment_client.list_data_paths():
        if file_name.startswith("Aabyssinian"):
            target_segment_client.copy_data(file_name, file_name, source_client=segment_client)

dataset_client.list_segment_names()
# test_1, test_2, trainval, abyssinian
dataset_client.commit("add abyssinian segment")
""""""

"""Move Data"""
import random

dataset_client.create_draft("draft-4")
val_segment_client = dataset_client.create_segment("val")
trainval_segment_client = dataset_client.get_segment("trainval")

# list_data_paths will return a lazy list, get and delete data are not supports at one time.
data_paths = list(trainval_segment_client.list_data_paths())

# Generate 500 random numbers.
val_randomlist = random.sample(range(0, len(data_paths)), 500)
for index in val_randomlist:
    file_name = data_paths[index]
    val_segment_client.move_data(file_name, file_name, source_client=trainval_segment_client)
dataset_client.move_segment("trainval", "train")

dataset_client.list_segment_names()
# train, val, test_1, test_2, abyssinian
dataset_client.commit("split train and val segment")
""""""
