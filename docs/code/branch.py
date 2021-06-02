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

"""Authorize a Dataset Client Instance"""
from tensorbay import GAS

ACCESS_KEY = "Accesskey-*****"
gas = GAS(ACCESS_KEY)
dataset_client = gas.create_dataset("DatasetName")
dataset_client.create_draft("draft-1")
# Add some data to the dataset.
dataset_client.commit("commit-1", tag="V1")
commit_id_1 = dataset_client.status.commit_id

dataset_client.create_draft("draft-2")
# Do some modifications to the dataset.
dataset_client.commit("commit-2", tag="V2")
commit_id_2 = dataset_client.status.commit_id

""""""

"""Create Branch"""
dataset_client.create_branch("T123")
""""""

"""Branch Name Will Be Stored"""
branch_name = dataset_client.status.branch_name
# branch_name = "T123"
commit_id = dataset_client.status.commit_id
# commit_id = "xxx"
""""""

"""Create Branch Based On a Revision"""
dataset_client.create_branch("T123", revision=commit_id_2)
dataset_client.create_branch("T123", revision="V2")
dataset_client.create_branch("T123", revision="main")
""""""

"""Branch Name Will Be Stored(Revision)"""
branch_name = dataset_client.status.branch_name
# branch_name = "T123"
commit_id = dataset_client.status.commit_id
# commit_id = "xxx"
""""""

"""Create Branch Based On a Former Commit"""
dataset_client.create_branch("T1234", revision=commit_id_1)
dataset_client.create_branch("T1234", revision="V1")
""""""

"""Branch Name Will Be Stored(Former Commit)"""
branch_name = dataset_client.status.branch_name
# branch_name = "T1234"
commit_id = dataset_client.status.commit_id
# commit_id = "xxx"
""""""

"""Create and Commit Draft"""
dataset_client.create_draft("draft-3")
# Do some modifications to the dataset.
dataset_client.commit("commit-3", tag="V3")
""""""

"""List Branches"""
branches = dataset_client.list_branches()
""""""

"""Get a Branch"""
branch = dataset_client.get_branch("T123")
""""""

"""Delete a Branch"""
dataset_client.delete_branch("T123")
""""""
