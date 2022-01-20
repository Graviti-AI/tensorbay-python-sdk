#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#

"""Interfaces about the branch."""

from typing import Any, Dict, Optional
from urllib.parse import urljoin

from graviti.client.request import PARTIAL_URL, open_api_do


def create_branch(
    url: str,
    access_key: str,
    dataset_id: str,
    name: str,
    commit: str,
) -> None:
    """Execute the OpenAPI `POST /v1/datasets{id}/branches`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        name: The name of the branch.
        commit: The information to locate the specific commit, which can be the commit id,
            the branch name, or the tag name.

    Examples:
        Create a branch with given name and commit:

        >>> create_branch(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     "branch-1",
        ...     "main"
        ... )

    """
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}/branches")
    post_data = {"name": name, "commit": commit}
    open_api_do(url, access_key, "POST", json=post_data)


def list_branches(
    url: str,
    access_key: str,
    dataset_id: str,
    *,
    name: Optional[str] = None,
    offset: int = 0,
    limit: int = 128,
) -> Dict[str, Any]:
    """Execute the OpenAPI `GET /v1/datasets{id}/branches`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        name: The name of the branch to be get.
        offset: The offset of the page.
        limit: The limit of the page.

    Examples:
        List branches:

        >>> list_branches(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68"
        ... )
        {
            "branches": [
                {
                    "name": "branch-1",
                    "commitId": "609d20c41252435fbee6c706f3bf1732",
                    "parentCommitId": "85c57a7f03804ccc906632248dc8c359",
                    "title": "commit-1",
                    "description": "",
                    "committer": {
                        "name": "czhual",
                        "date": 1643013213
                    }
                },
                {
                    "name": "main",
                    "commitId": "85c57a7f03804ccc906632248dc8c359",
                    "parentCommitId": "784ba0d3bf0a41f6a7bfd771d8c00fcb",
                    "title": "upload data",
                    "description": "",
                    "committer": {
                        "name": "Gravitier",
                        "date": 1641404774
                    }
                }
            ],
            "offset": 0,
            "recordSize": 2,
            "totalCount": 2
        }

        Get the branch with the given name:

        >>> list_branches(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     name="branch-1"
        ... )
        {
            "branches": [
                {
                    "name": "branch-1",
                    "commitId": "609d20c41252435fbee6c706f3bf1732",
                    "parentCommitId": "85c57a7f03804ccc906632248dc8c359",
                    "title": "commit-1",
                    "description": "",
                    "committer": {
                        "name": "czhual",
                        "date": 1643013213
                    }
                }
            ],
            "offset": 0,
            "recordSize": 1,
            "totalCount": 1
        }

    Returns:
        The response of OpenAPI.

    """
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}/branches")
    params: Dict[str, Any] = {"offset": offset, "limit": limit}
    if name:
        params["name"] = name
    return open_api_do(url, access_key, "GET", params=params).json()  # type: ignore[no-any-return]


def delete_branch(
    url: str,
    access_key: str,
    dataset_id: str,
    name: str,
) -> None:
    """Execute the OpenAPI `DELETE /v1/datasets{id}/branches`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        name: The name of the branch.

    Examples:
        Delete the branch with the given name:

        >>> delete_branch(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     "branch-1",
        ... )

    """
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}/branches")
    delete_data = {"name": name}
    open_api_do(url, access_key, "DELETE", json=delete_data)
