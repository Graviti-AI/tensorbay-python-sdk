#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#

"""Interfaces about data."""

from typing import Any, Dict, Optional


def list_data(  # pylint: disable=unused-argument, too-many-arguments
    url: str,
    access_key: str,
    dataset_id: str,
    segment_name: str,
    *,
    draft_number: Optional[int] = None,
    commit: Optional[str] = None,
    offset: int = 0,
    limit: int = 128,
) -> Dict[str, Any]:
    """Execute the OpenAPI `GET /v1/datasets{id}/data`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        segment_name: The name of the segment.
        draft_number: The draft number.
        commit: The information to locate the specific commit, which can be the commit id,
            the branch name, or the tag name.
        offset: The offset of the page.
        limit: The limit of the page.

    Return:
        The response of OpenAPI.

    """


def list_data_details(  # pylint: disable=unused-argument
    url: str,
    access_key: str,
    dataset_id: str,
    segment_name: str,
    *,
    draft_number: Optional[int] = None,
    commit: Optional[str] = None,
    remote_path: Optional[str] = None,
    is_internal: bool = False,
    offset: int = 0,
    limit: int = 128,
) -> Dict[str, Any]:
    """Execute the OpenAPI `GET /v1/datasets{id}/data/details`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        segment_name: The name of the segment.
        draft_number: The draft number.
        commit: The information to locate the specific commit, which can be the commit id,
            the branch name, or the tag name.
        remote_path: The remote path of the data.
        is_internal: Whether the request is from internal.
        offset: The offset of the page.
        limit: The limit of the page.

    Return:
        The response of OpenAPI.

    """


def list_data_urls(  # pylint: disable=unused-argument
    url: str,
    access_key: str,
    dataset_id: str,
    segment_name: str,
    *,
    draft_number: Optional[int] = None,
    commit: Optional[str] = None,
    remote_path: Optional[str] = None,
    is_internal: bool = False,
    offset: int = 0,
    limit: int = 128,
) -> Dict[str, Any]:
    """Execute the OpenAPI `GET /v1/datasets{id}/data/urls`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        segment_name: The name of the segment.
        draft_number: The draft number.
        commit: The information to locate the specific commit, which can be the commit id,
            the branch name, or the tag name.
        remote_path: The remote path of the data.
        is_internal: Whether the request is from internal.
        offset: The offset of the page.
        limit: The limit of the page.

    Return:
        The response of OpenAPI.

    """


def list_mask_urls(  # pylint: disable=unused-argument
    url: str,
    access_key: str,
    dataset_id: str,
    segment_name: str,
    mask_type: str,
    *,
    draft_number: Optional[int] = None,
    commit: Optional[str] = None,
    remote_path: Optional[str] = None,
    is_internal: bool = False,
    offset: int = 0,
    limit: int = 128,
) -> Dict[str, Any]:
    """Execute the OpenAPI `GET /v1/datasets{id}/mask/urls`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        segment_name: The name of the segment.
        mask_type: The required mask type, the supported types are ``SEMANTIC_MASK``,
            ``INSTANCE_MASK`` and ``PANOPTIC_MASK``
        draft_number: The draft number.
        commit: The information to locate the specific commit, which can be the commit id,
            the branch name, or the tag name.
        remote_path: The remote path of the data.
        is_internal: Whether the request is from internal.
        offset: The offset of the page.
        limit: The limit of the page.

    Return:
        The response of OpenAPI.

    """
