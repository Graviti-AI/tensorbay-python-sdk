#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Interfaces about the draft."""

from typing import Any, Dict, Optional
from urllib.parse import urljoin

from graviti.client.request import PARTIAL_URL, open_api_do


def create_draft(
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

    Examples:
        Create a draft on the given branch name:

        >>> create_draft(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     "main",
        ...     "draft-2"
        ... )
        {
            "draftNumber": 2
        }

    Returns:
        The response of OpenAPI.

    """
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}/drafts")
    post_data = {"branchName": branch_name, "title": title}

    if description:
        post_data["description"] = description

    return open_api_do(  # type: ignore[no-any-return]
        url, access_key, "POST", json=post_data
    ).json()


def list_drafts(
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

    Examples:
        List drafts with the given status and branch name:

        >>> list_drafts(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ... )
        {
            "drafts": [
                {
                    "number": 2,
                    "title": "branch-2",
                    "description": "",
                    "branchName": "main",
                    "status": "OPEN",
                    "parentCommitId": "85c57a7f03804ccc906632248dc8c359",
                    "author": {
                        "name": "czhual",
                        "date": 1643013702
                    },
                    "updatedAt": 1643013702
                }
            ],
            "offset": 0,
            "recordSize": 1,
            "totalCount": 1
        }

    Returns:
        The response of OpenAPI.

    """
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}/drafts")
    params: Dict[str, Any] = {"status": status, "offset": offset, "limit": limit}

    if branch_name:
        params["branchName"] = branch_name

    return open_api_do(url, access_key, "GET", params=params).json()  # type: ignore[no-any-return]


def update_draft(
    url: str,
    access_key: str,
    dataset_id: str,
    draft_number: int,
    *,
    status: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> None:
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

    Examples:
        Update the title or description of the draft:

        >>> update_draft(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     2,
        ...     title="draft-3"
        ... )

        Close the draft:

        >>> update_draft(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     2,
        ...     status="CLOSED"
        ... )

    """
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}/drafts/{draft_number}")
    patch_data: Dict[str, Any] = {"draftNumber": draft_number}

    if status:
        patch_data["status"] = status
    if title is not None:
        patch_data["title"] = title
    if description is not None:
        patch_data["description"] = description

    open_api_do(url, access_key, "PATCH", json=patch_data)
