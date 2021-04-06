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


"""This file includes the python code of tag.rst."""

"""Authorize a Dataset Client Object"""
from tensorbay import GAS

ACCESS_KEY = "Accesskey-*****"
gas = GAS(ACCESS_KEY)
dataset_client = gas.create_dataset("DatasetName")
dataset_client.create_draft("draft-1")
dataset_client.commit("commit-1")
""""""

"""Create Tag"""
dataset_client.create_tag("Tag-1")
""""""

"""Delete Tag"""
dataset_client.delete_tag("Tag-1")
""""""

"""Create Tag When Committing"""
dataset_client.create_draft("draft-2")
dataset_client.commit("commit-2", tag="Tag-1")
""""""

"""Get Tag"""
tag = dataset_client.get_tag("Tag-1")
""""""

"""List Tags"""
tags = list(dataset_client.list_tags())
""""""
