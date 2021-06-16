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


"""This file includes the python code of draft_and_commit.rst."""

"""Authorize a Dataset Client Instance"""
from tensorbay import GAS

ACCESS_KEY = "Accesskey-*****"
gas = GAS(ACCESS_KEY)
dataset_client = gas.create_dataset("DatasetName")
""""""

"""Create Draft"""
dataset_client.create_draft("draft-1")
""""""

"""Draft Number Will Be Stored"""
is_draft = dataset_client.status.is_draft
# is_draft = True (True for draft, False for commit)
draft_number = dataset_client.status.draft_number
# draft_number = 1
branch_name = dataset_client.status.branch_name
# branch_name = main
""""""

"""Create Draft on a Branch"""
dataset_client.create_draft("draft-1", branch_name="main")
""""""

"""List Drafts"""
drafts = dataset_client.list_drafts()
""""""

"""Get Draft"""
draft = dataset_client.get_draft(draft_number=1)
""""""

"""Commit Draft"""
dataset_client.commit("commit-1", "commit description")
is_draft = dataset_client.status.is_draft
# is_draft = False (True for draft, False for commit)
commit_id = dataset_client.status.commit_id
# commit_id = "***"
""""""

"""List Commits"""
commits = dataset_client.list_commits()
""""""

"""Get Commit"""
commit = dataset_client.get_commit(commit_id)
""""""

"""Checkout"""
# checkout to the draft.
dataset_client.checkout(draft_number=draft_number)
# checkout to the commit.
dataset_client.checkout(revision=commit_id)
""""""
