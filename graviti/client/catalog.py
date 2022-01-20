#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#

"""Interfaces about the catalog."""

from typing import Any, Dict, Optional
from urllib.parse import urljoin

from graviti.client.request import PARTIAL_URL, open_api_do


def get_catalog(
    url: str,
    access_key: str,
    dataset_id: str,
    *,
    draft_number: Optional[int] = None,
    commit: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute the OpenAPI `GET /v1/datasets{id}/labels/catalogs`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        draft_number: The draft number.
        commit: The information to locate the specific commit, which can be the commit id,
            the branch name, or the tag name.

    Examples:
        Get the catalog of the dataset with the given id and commit/draft_number:

        >>> get_catalog(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     commit="main"
        ... )
        {
            "catalog": {
                "BOX2D": {
                    "description": "",
                    "isTracking": false
                },
                "CLASSIFICATION": {
                    "categories": [
                        {
                            "description": "",
                            "name": "Cat.Abyssinian"
                        },
                        {
                            "description": "",
                            "name": "Cat.Bengal"
                        },
                        ...
                    ],
                    "description": ""
                },
                "SEMANTIC_MASK": {
                    "categories": [
                        {
                            "categoryId": 1,
                            "description": "",
                            "name": "foreground"
                        },
                        {
                            "categoryId": 2,
                            "description": "",
                            "name": "background"
                        },
                        {
                            "categoryId": 3,
                            "description": "",
                            "name": "contour"
                        }
                    ],
                    "description": ""
                }
            }
        }

    Returns:
        The response of OpenAPI.

    """
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}/labels/catalogs")
    params: Dict[str, Any] = {}
    if draft_number:
        params["draftNumber"] = draft_number
    if commit:
        params["commit"] = commit
    return open_api_do(url, access_key, "GET", params=params).json()  # type: ignore[no-any-return]
