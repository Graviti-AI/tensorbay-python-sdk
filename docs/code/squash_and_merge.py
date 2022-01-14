#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=pointless-string-statement
# pylint: disable=pointless-statement
# pylint: disable=invalid-name
# type: ignore[attr-defined]
# https://github.com/python/mypy/issues/5858

"""This file includes the python code of squash_and_merge.rst."""

"""Authorize a Dataset Client Instance"""
from tensorbay import GAS

gas = GAS("<YOUR_ACCESSKEY>")
dataset_client = gas.create_dataset("<DATASET_NAME>")

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

"""Create Job"""
job = dataset_client.squash_and_merge.create_job(
    draft_title="draft-5",
    source_branch_name="dev",
    target_branch_name="main",
    draft_description="draft_description",
    strategy="override",
)
""""""

"""Checkout First"""
job = dataset_client.squash_and_merge.create_job(
    draft_title="draft-5",
    source_branch_name="dev",
    draft_description="draft_description",
    strategy="override",
)
""""""

"""Get, List and Delete"""
job = dataset_client.squash_and_merge.get_job("jobId")
dataset_client.squash_and_merge.delete_job("jobId")
job = dataset_client.squash_and_merge.list_jobs()[0]
""""""

"""Get Job Info"""
job.status
job.result
job.error_message
job.arguments
""""""

"""Update Job"""
job.update()
job.update(until_complete=True)
""""""

"""Abort and Retry Job"""
job.abort()
job.retry()
""""""
