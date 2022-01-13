#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#

"""Interfaces about the commit."""

from typing import Any, Dict, Optional


def commit_draft(  # pylint: disable=unused-argument
    url: str,
    access_key: str,
    dataset_id: str,
    draft_number: int,
    title: str,
    *,
    description: Optional[str] = None,
    tag: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute the OpenAPI `POST /v1/datasets{id}/commits`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        draft_number: The draft number.
        title: The draft title.
        description: The draft description.
        tag: The tag name.

    Return:
        The response of OpenAPI.

    """


def list_commits(  # pylint: disable=unused-argument
    url: str,
    access_key: str,
    dataset_id: str,
    *,
    commit: Optional[str] = None,
    offset: int = 0,
    limit: int = 128,
) -> Dict[str, Any]:
    """Execute the OpenAPI `GET /v1/datasets{id}/commits`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        commit: The information to locate the specific commit, which can be the commit id,
            the branch name, or the tag name.
        offset: The offset of the page.
        limit: The limit of the page.

    Return:
        The response of OpenAPI.

    """
