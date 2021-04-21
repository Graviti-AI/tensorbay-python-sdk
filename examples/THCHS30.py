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
# pylint: disable=unused-import
# flake8: noqa: F401

"""This file includes the python code of THCHS.rst and read_dataset_class.rst."""

"""Authorize a Client Instance"""
from tensorbay import GAS

ACCESS_KEY = "Accesskey-*****"
gas = GAS(ACCESS_KEY)
""""""

"""Create Dataset"""
gas.create_dataset("THCHS-30")
""""""

"""Organize Dataset / regular import"""
from tensorbay.dataset import Data, Dataset
from tensorbay.label import LabeledSentence, SentenceSubcatalog, Word

""""""

"""Organize dataset / import dataloader"""
from tensorbay.opendataset import THCHS30

dataset = THCHS30("path/to/dataset/directory")
""""""

"""Upload Dataset"""
dataset_client = gas.upload_dataset(dataset)
dataset_client.commit("initial commit")
""""""

"""Read Dataset / get dataset"""
dataset_client = gas.get_dataset("THCHS-30")
""""""

"""Read Dataset / list segment names"""
dataset_client.list_segment_names()
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
