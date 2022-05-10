#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=pointless-string-statement
# pylint: disable=invalid-name


"""This file includes the python code of diff.rst."""

"""Authorize a Dataset Client Instance"""
from tensorbay import GAS

# Please visit `https://gas.graviti.com/tensorbay/developer` to get the AccessKey.
gas = GAS("<YOUR_ACCESSKEY>")
dataset_client = gas.create_dataset("<DATASET_NAME>")
dataset_client.create_draft("draft-1")
# Add some data to the dataset.
dataset_client.commit("commit-1", tag="V1")
commit_id_1 = dataset_client.status.commit_id

dataset_client.create_draft("draft-2")
# Do some modifications to the dataset.
dataset_client.commit("commit-2", tag="V2")
commit_id_2 = dataset_client.status.commit_id

dataset_client.create_draft("draft-3")
draft_number_3 = dataset_client.status.draft_number
head = ""

""""""

"""Get Diff"""
diff = dataset_client.get_diff(head=head)
""""""

"""Get Diff on Commit"""
diff = dataset_client.get_diff(head="3bc35d806e0347d08fc23564b82737dc")
""""""

"""Get Diff on Draft"""
diff = dataset_client.get_diff(head=1)
""""""
