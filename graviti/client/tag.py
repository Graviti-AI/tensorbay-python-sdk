#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Interfaces about the tag."""

from typing import Any, Dict, Optional


def create_tag(  # pylint: disable=unused-argument
    url: str,
    access_key: str,
    dataset_id: str,
    name: str,
    commit: str,
) -> Dict[str, Any]:
    """Execute the OpenAPI `POST /v1/datasets{id}/tags`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        name: The tag name to be created for the specific commit.
        commit: The information to locate the specific commit, which can be the commit id,
            the branch name, or the tag name.

    Return:
        The response of OpenAPI.

    """


def list_tags(  # pylint: disable=unused-argument
    url: str,
    access_key: str,
    dataset_id: str,
    *,
    name: Optional[str] = None,
    offset: int = 0,
    limit: int = 128,
) -> Dict[str, Any]:
    """Execute the OpenAPI `GET /v1/datasets{id}/tags`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        name: The name of the tag to be get.
        offset: The offset of the page.
        limit: The limit of the page.

    Return:
        The response of OpenAPI.

    """


def delete_tag(  # pylint: disable=unused-argument
    url: str,
    access_key: str,
    dataset_id: str,
    name: str,
) -> Dict[str, Any]:
    """Execute the OpenAPI `DELETE /v1/datasets{id}/tags`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        name: The name of the tag to be deleted.

    Return:
        The response of OpenAPI.

    """
