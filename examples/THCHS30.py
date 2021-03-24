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

"""This file includes the python code of THCHS.rst and read_dataset_class.rst."""

"""Authorize a Client Object"""
from tensorbay import GAS

ACCESS_KEY = "Accesskey-*****"
gas = GAS(ACCESS_KEY)
""""""

"""Create Dataset"""
gas.create_dataset("THCHS-30")
""""""

"""List Dataset Names"""
list(gas.list_dataset_names())
""""""


from tensorbay.opendataset import THCHS30

dataset = THCHS30("path/to/dataset/directory")


"""Upload Dataset"""
# dataset is the one you initialized in "Organize Dataset" section
dataset_client = gas.upload_dataset(dataset, jobs=8, skip_uploaded_files=False)
dataset_client.commit("THCHS-30")
""""""

"""Read Dataset / get dataset"""
dataset_client = gas.get_dataset("THCHS-30")
""""""

"""Read Dataset / list segment names"""
list(dataset_client.list_segment_names())
""""""

"""Read Dataset / get segment"""
from tensorbay.dataset import Segment

dev_segment = Segment("dev", dataset_client)
""""""

"""Read Dataset / get data"""
data = dev_segment[0]
""""""

"""Read Dataset / get label"""
labeled_sentence = data.label.sentence[0]
sentence = labeled_sentence.sentence
spell = labeled_sentence.spell
phone = labeled_sentence.phone
""""""

"""Delete Dataset"""
gas.delete_dataset("THCHS-30")
""""""
