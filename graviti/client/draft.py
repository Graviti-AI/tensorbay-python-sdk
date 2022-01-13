#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Interfaces about the draft."""

from typing import Any, Dict, Optional


def create_draft(  # pylint: disable=unused-argument
    url: str,
    access_key: str,
    dataset_id: str,
    branch_name: str,
    title: str,
    *,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute the OpenAPI `POST /v1/datasets{id}/drafts`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        branch_name: The branch name.
        title: The draft title.
        description: The draft description.

    Return:
        The response of OpenAPI.

    """


def list_drafts(  # pylint: disable=unused-argument
    url: str,
    access_key: str,
    dataset_id: str,
    *,
    status: Optional[str] = "OPEN",
    branch_name: Optional[str] = None,
    offset: int = 0,
    limit: int = 128,
) -> Dict[str, Any]:
    """Execute the OpenAPI `GET /v1/datasets{id}/drafts`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        status: The draft status which includes "OPEN", "CLOSED", "COMMITTED", "ALL" and None.
            where None means listing open drafts.
        branch_name: The branch name.
        offset: The offset of the page.
        limit: The limit of the page.

    Return:
        The response of OpenAPI.

    """


def update_draft(  # pylint: disable=unused-argument
    url: str,
    access_key: str,
    dataset_id: str,
    draft_number: int,
    status: str,
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute the OpenAPI `PATCH /v1/datasets{id}/drafts{draftNumber}`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        draft_number: The updated draft number.
        status: The draft status which includes "OPEN", "CLOSED", "COMMITTED", "ALL" and None.
            where None means listing open drafts.
        title: The draft title.
        description: The draft description.

    Return:
        The response of OpenAPI.

    """
