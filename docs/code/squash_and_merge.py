#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=pointless-string-statement
# pylint: disable=invalid-name


"""This file includes the python code of squash_and_merge.rst."""

"""Authorize a Dataset Client Instance"""
from tensorbay import GAS

ACCESS_KEY = "Accesskey-*****"
gas = GAS(ACCESS_KEY)
dataset_client = gas.create_dataset("DatasetName")

dataset_client.create_draft("draft-1")
dataset_client.commit("commit-1")

dataset_client.create_branch("dev")
dataset_client.create_draft("draft-2")
dataset_client.commit("commit-2")

dataset_client.create_draft("draft-3")
dataset_client.commit("commit-3")

dataset_client.checkout("main")
dataset_client.create_draft("draft-4")
dataset_client.commit("commit-4")
""""""

"""Squash and Merge"""
draft_number = dataset_client.squash_and_merge(
    "draft-5",
    description="description",
    source_branch_name="dev",
    target_branch_name="main",
    strategy="override",
)
dataset_client.checkout(draft_number=draft_number)
dataset_client.commit("commit-5")
""""""

"""Checkout First"""
draft_number = dataset_client.squash_and_merge(
    "draft-5",
    description="description",
    source_branch_name="dev",
    strategy="override",
)
dataset_client.checkout(draft_number=draft_number)
dataset_client.commit("commit-5")
""""""
