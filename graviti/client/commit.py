#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#

"""Interfaces about the commit."""

from typing import Any, Dict, Optional
from urllib.parse import urljoin

from graviti.client.request import PARTIAL_URL, open_api_do


def commit_draft(
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

    Examples:
        Commit the draft with the given draft number:

        >>> commit_draft(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     2,
        ...     "commit-2",
        ... )
        {
            "commitId": "a0d4065872f245e4ad1d0d1186e3d397"
        }

    Returns:
        The response of OpenAPI.

    """
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}/commits")
    post_data: Dict[str, Any] = {"title": title, "draftNumber": draft_number}

    if description:
        post_data["description"] = description
    if tag:
        post_data["tag"] = tag

    return open_api_do(  # type: ignore[no-any-return]
        url, access_key, "POST", json=post_data
    ).json()


def list_commits(
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

    Examples:
        List commits:

        >>> list_commits(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ... )
        {
            "commits": [
                {
                    "commitId": "a0d4065872f245e4ad1d0d1186e3d397",
                    "parentCommitId": "85c57a7f03804ccc906632248dc8c359",
                    "title": "commit-2",
                    "description": "",
                    "committer": {
                        "name": "czhual",
                        "date": 1643013945
                    },
                    "dataCount": 7390
                },
                {
                    "commitId": "85c57a7f03804ccc906632248dc8c359",
                    "parentCommitId": "784ba0d3bf0a41f6a7bfd771d8c00fcb",
                    "title": "upload data",
                    "description": "",
                    "committer": {
                        "name": "Gravitier",
                        "date": 1641404774
                    },
                    "dataCount": 7390
                },
                {
                    "commitId": "784ba0d3bf0a41f6a7bfd771d8c00fcb",
                    "parentCommitId": "00000000000000000000000000000000",
                    "title": "update tags",
                    "description": "",
                    "committer": {
                        "name": "Gravitier",
                        "date": 1641404362
                    },
                    "dataCount": 0
                }
            ],
            "offset": 0,
            "recordSize": 3,
            "totalCount": 3
        }

    Returns:
        The response of OpenAPI.

    """
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}/commits")
    params: Dict[str, Any] = {"offset": offset, "limit": limit}
    if commit:
        params["commit"] = commit
    return open_api_do(url, access_key, "GET", params=params).json()  # type: ignore[no-any-return]
