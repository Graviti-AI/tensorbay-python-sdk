#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
"""Client module."""

from graviti.client.branch import create_branch, delete_branch, list_branches
from graviti.client.catalog import get_catalog
from graviti.client.commit import commit_draft, list_commits
from graviti.client.data import list_data, list_data_details, list_data_urls, list_mask_urls
from graviti.client.dataset import get_dataset, get_total_size, list_datasets
from graviti.client.draft import create_draft, list_drafts, update_draft
from graviti.client.label import get_label_statistics
from graviti.client.notes import get_notes
from graviti.client.segment import list_segments
from graviti.client.tag import create_tag, delete_tag, list_tags
from graviti.client.user import get_user

__all__ = [
    "commit_draft",
    "create_branch",
    "create_draft",
    "create_tag",
    "delete_branch",
    "delete_tag",
    "get_catalog",
    "get_dataset",
    "get_label_statistics",
    "get_notes",
    "get_total_size",
    "get_user",
    "list_branches",
    "list_commits",
    "list_data",
    "list_datasets",
    "list_data_details",
    "list_data_urls",
    "list_drafts",
    "list_mask_urls",
    "list_segments",
    "list_tags",
    "update_draft",
]
