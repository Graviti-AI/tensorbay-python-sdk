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

"""This file includes the python code of NewsGroups.rst and read_dataset_class.rst."""

"""Authorize a Client Object"""
from tensorbay import GAS

ACCESS_KEY = "Accesskey-*****"
gas = GAS(ACCESS_KEY)
""""""

"""Create Dataset"""
gas.create_dataset("20 Newsgroups")
""""""

"""List Dataset Names"""
list(gas.list_dataset_names())
""""""


from tensorbay.opendataset import Newsgroups20

dataset = Newsgroups20("path/to/dataset/directory")


"""Upload Dataset"""
# dataset is the one you initialized in "Organize Dataset" section
dataset_client = gas.upload_dataset(dataset, jobs=8, skip_uploaded_files=False)
dataset_client.commit("20 Newsgroups")
""""""

"""Read Dataset / get dataset"""
dataset_client = gas.get_dataset("20 Newsgroups")
""""""

"""Read Dataset / list segment names"""
list(dataset_client.list_segment_names())
""""""

"""Read Dataset / get segment"""
from tensorbay.dataset import Segment

segment_20news_18828 = Segment("20news-18828", dataset_client)
""""""

"""Read Dataset / get data"""
data = segment_20news_18828[0]
""""""

"""Read Dataset / get label"""
category = data.label.classification.category
""""""

"""Delete Dataset"""
gas.delete_dataset("20 Newsgroups")
""""""
