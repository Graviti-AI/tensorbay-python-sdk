#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=pointless-string-statement
# pylint: disable=invalid-name
# pylint: disable=unsubscriptable-object
# flake8: noqa: F401

"""This file includes the python code of THCHS.rst and read_dataset_class.rst."""

"""Authorize a Client Instance"""
from tensorbay import GAS

gas = GAS("<YOUR_ACCESSKEY>")
""""""

"""Create Dataset"""
gas.create_dataset("THCHS-30")
""""""

"""Organize Dataset / regular import"""
from tensorbay.dataset import Dataset

""""""

"""Organize dataset / import dataloader"""
from tensorbay.opendataset import THCHS30

dataset = THCHS30("<path/to/dataset>")
""""""

"""Upload Dataset"""
dataset_client = gas.upload_dataset(dataset, jobs=8)
dataset_client.commit("initial commit")
""""""

"""Read Dataset / get dataset"""
dataset = Dataset("THCHS-30", gas)
""""""

"""Read Dataset / list segment names"""
dataset.keys()
""""""

"""Read Dataset / get segment"""
segment = dataset["dev"]
""""""

"""Read Dataset / get data"""
data = segment[0]
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
