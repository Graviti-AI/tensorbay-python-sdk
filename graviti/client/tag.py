#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Interfaces about the tag."""

from typing import Any, Dict, Optional
from urllib.parse import urljoin

from graviti.client.request import PARTIAL_URL, open_api_do


def create_tag(
    url: str,
    access_key: str,
    dataset_id: str,
    name: str,
    commit: str,
) -> None:
    """Execute the OpenAPI `POST /v1/datasets{id}/tags`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        name: The tag name to be created for the specific commit.
        commit: The information to locate the specific commit, which can be the commit id,
            the branch name, or the tag name.

    Examples:
        Create a tag with the given commit:

        >>> create_tag(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     "tag-1",
        ...     "main"
        ... )

    """
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}/tags")
    post_data = {"name": name, "commit": commit}
    open_api_do(url, access_key, "POST", json=post_data)


def list_tags(
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

    Examples:
        List tags:

        >>> list_tags(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68"
        ... )
        {
            "tags": [
                {
                    "name": "tag-1",
                    "commitId": "a0d4065872f245e4ad1d0d1186e3d397",
                    "parentCommitId": "85c57a7f03804ccc906632248dc8c359",
                    "title": "commit-2",
                    "description": "",
                    "committer": {
                        "name": "czhual",
                        "date": 1643013945
                    }
                },
                {
                    "name": "tag-2",
                    "commitId": "986d8ea00da842ed85dd5d5cd14b5aef",
                    "parentCommitId": "a0d4065872f245e4ad1d0d1186e3d397",
                    "title": "commit-1",
                    "description": "",
                    "committer": {
                        "name": "czhual",
                        "date": 1643015489
                    }
                }
            ],
            "offset": 0,
            "recordSize": 2,
            "totalCount": 2
        }

        Get the tag with the given name:

        >>> list_tags(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     name="tag-1"
        ... )
        {
            "tags": [
                {
                    "name": "tag-1",
                    "commitId": "a0d4065872f245e4ad1d0d1186e3d397",
                    "parentCommitId": "85c57a7f03804ccc906632248dc8c359",
                    "title": "commit-2",
                    "description": "",
                    "committer": {
                        "name": "czhual",
                        "date": 1643013945
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
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}/tags")

    params: Dict[str, Any] = {"offset": offset, "limit": limit}
    if name:
        params["name"] = name

    return open_api_do(url, access_key, "GET", params=params).json()  # type: ignore[no-any-return]


def delete_tag(
    url: str,
    access_key: str,
    dataset_id: str,
    name: str,
) -> None:
    """Execute the OpenAPI `DELETE /v1/datasets{id}/tags`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        name: The name of the tag to be deleted.

    Examples:
        Delete the tag with the given name:

        >>> delete_tag(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     "tag-2"
        ... )

    """
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}/tags")
    delete_data = {"name": name}
    open_api_do(url, access_key, "DELETE", json=delete_data)
