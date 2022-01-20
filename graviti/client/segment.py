#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Interfaces about the segment."""

from typing import Any, Dict, Optional
from urllib.parse import urljoin

from graviti.client.request import PARTIAL_URL, open_api_do


def list_segments(
    url: str,
    access_key: str,
    dataset_id: str,
    *,
    draft_number: Optional[int] = None,
    commit: Optional[str] = None,
    offset: int = 0,
    limit: int = 128,
) -> Dict[str, Any]:
    """Execute the OpenAPI `GET /v1/datasets{id}/segments`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        draft_number: The draft number.
        commit: The information to locate the specific commit, which can be the commit id,
            the branch name, or the tag name.
        offset: The offset of the page.
        limit: The limit of the page.

    Examples:
        List segments of the dataset with the given id and commit/draft_number:

        >>> list_segments(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     "test",
        ...     commit="main"
        ... )
        {
            "segments": [
                {
                    "name": "test",
                    "description": ""
                },
                {
                    "name": "trainval",
                    "description": ""
                }
            ],
            "offset": 0,
            "recordSize": 2,
            "totalCount": 2
        }

    Returns:
        The response of OpenAPI.

    """
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}/segments")
    params: Dict[str, Any] = {"offset": offset, "limit": limit}

    if draft_number:
        params["draftNumber"] = draft_number
    if commit:
        params["commit"] = commit

    return open_api_do(url, access_key, "GET", params=params).json()  # type: ignore[no-any-return]
