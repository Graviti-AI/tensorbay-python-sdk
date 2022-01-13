#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Interfaces about the dataset."""

from typing import Any, Dict, Optional


def get_dataset(
    url: str, access_key: str, dataset_id: str  # pylint: disable=unused-argument
) -> Dict[str, Any]:
    """Execute the OpenAPI `GET /v1/datasets{id}`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.

    Examples:
        >>> response = get_dataset("<URL>", "<YOUR_ACCESSKEY>", "<DATASET_ID>")
        >>> response.json()
        {
            "name": "<DATASET_NAME>",
            "alias": "<DATASET_ALIAS>",
            "type": 0,
            "defaultBranch": "main",
            "updateTime": 1641542018,
            "owner": "<OWNER_NIKENAME>",
            "commitId": "<COMMIT_ID>",
            "coverUrl": "<COVER_URL>",
            "isPublic": True,
            "configName": "AliCloud-oss-cn-shanghai"
        }

    Return:
        The response of OpenAPI.

    """


def list_datasets(  # pylint: disable=unused-argument
    url: str,
    access_key: str,
    *,
    name: Optional[str] = None,
    offset: int = 0,
    limit: int = 128,
) -> Dict[str, Any]:
    """Execute the OpenAPI `GET /v1/datasets`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        name: The name of the dataset to be get.
        offset: The offset of the page.
        limit: The limit of the page.

    Examples:
        >>> response = list_datasets("<URL>", "<YOUR_ACCESSKEY>")
        >>> response.json()
        {
            "datasets": [
                {
                    "id": "<DATASET_ID>",
                    "name": "<DATASET_NAME>",
                    "alias": "<DATASET_ALIAS>",
                    "type": 0,
                    "defaultBranch": "main",
                    "commitId": "<COMMIT_ID>",
                    "coverUrl": "<COVER_URL>",
                    "dataCount": 70000,
                    "dataSize": 19254372,
                    "updateTime": 1641542018,
                    "owner": "<OWNER_NIKENAME>",
                    "tabs": {
                        "dataType": [
                            {
                                "id": "c923e46784d64ec08ba17afb266bbc9f",
                                "name": "Image"
                            }
                        ],
                        "labelType": [
                            {
                                "id": "87b207c5984546a6b980615288f1913e",
                                "name": "Classification"
                            }
                        ],
                        "usedScene": [
                            {
                                "id": "608f93b5f2614f9dbf9127c348494651",
                                "name": "MNIST"
                            }
                        ]
                    }
                }
            ],
            "offset": 0,
            "recordSize": 1,
            "totalCount": 1
        }

    Return:
        The response of OpenAPI.

    """


def get_total_size(  # pylint: disable=unused-argument
    url: str,
    access_key: str,
    dataset_id: str,
    commit: str,
) -> Dict[str, Any]:
    """Execute the OpenAPI `GET /v1/datasets{id}/total-size`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        commit: The information to locate the specific commit, which can be the commit id,
            the branch name, or the tag name.

    Return:
        The response of OpenAPI.

    """
