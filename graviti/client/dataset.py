#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Interfaces about the dataset."""

from typing import Any, Dict, Optional
from urllib.parse import urljoin

from graviti.client.request import PARTIAL_URL, open_api_do


def get_dataset(url: str, access_key: str, dataset_id: str) -> Dict[str, Any]:
    """Execute the OpenAPI `GET /v1/datasets{id}`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.

    Examples:
        Get the dataset with the given dataset id:

        >>> get_dataset(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68"
        ... )
        {
            "name": "OxfordIIITPet",
            "alias": "Oxford-IIIT Pet",
            "type": 0,
            "defaultBranch": "main",
            "updateTime": 1643015490,
            "owner": "czhual",
            "commitId": "a0d4065872f245e4ad1d0d1186e3d397",
            "coverUrl": "https://tutu.s3.cn-northwest-1.amazonaws.com.cn/
                openDatasetImages_new_V4/OxfordIIITPet/cover-OxfordIIITPet.jpg",
            "isPublic": True,
            "configName": ""
        }

    Returns:
        The response of OpenAPI.

    """
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}")
    return open_api_do(url, access_key, "GET").json()  # type: ignore[no-any-return]


def list_datasets(
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
        List datasets:

        >>> list_datasets("https://gas.graviti.com/", "ACCESSKEY-********")
        {
            "datasets": [
                {
                    "id": "2bc95d506db2401b898067f1045d7f68",
                    "name": "OxfordIIITPet",
                    "alias": "Oxford-IIIT Pet",
                    "type": 0,
                    "defaultBranch": "main",
                    "commitId": "a0d4065872f245e4ad1d0d1186e3d397",
                    "coverUrl": "https://tutu.s3.cn-northwest-1.amazonaws.com.cn/
                        openDatasetImages_new_V4/OxfordIIITPet/cover-OxfordIIITPet.jpg",
                    "dataCount": 7390,
                    "dataSize": 791309002,
                    "updateTime": 1643015490,
                    "owner": "czhual",
                    "tabs": {
                        "dataType": [
                            {
                                "id": "69fe9a0fd4da42f9bf2ce4cd8ece8cbc",
                                "name": "Image"
                            }
                        ],
                        "labelType": [
                            {
                                "id": "5afe36dbefe74801a0ed264b438c0c9b",
                                "name": "Box2D"
                            },
                            {
                                "id": "9c156d3aa81646d18946873de5f2db20",
                                "name": "Classification"
                            },
                            {
                                "id": "c21ba730553d4729a9411a0843e2bcde",
                                "name": "SemanticMask"
                            }
                        ],
                        "usedScene": [
                            {
                                "id": "83aff47fcde14ae5a67ea12950333b71",
                                "name": "Animal"
                            }
                        ]
                    }
                },
                {
                    "id": "bde36c12e6854fc8a5d9913faffb2b53",
                    "name": "CCPD",
                    "alias": "CCPD",
                    "type": 0,
                    "defaultBranch": "main",
                    "commitId": "dd2ec2690dde4d6f9328518059fd5eb8",
                    "coverUrl": "https://tutu.s3.cn-northwest-1.amazonaws.com.cn/
                        openDatasetImages_new_V4/CCPD/cover-CCPD.jpg",
                    "dataCount": 355013,
                    "dataSize": 22379147417,
                    "updateTime": 1642992029,
                    "owner": "czhual",
                    "tabs": {
                        "dataType": [
                            {
                                "id": "69fe9a0fd4da42f9bf2ce4cd8ece8cbc",
                                "name": "Image"
                            }
                        ],
                        "labelType": [
                            {
                                "id": "5fad71b2f062414ab99f62ff7c9a67c9",
                                "name": "Polygon2D"
                            }
                        ],
                        "taskType": [
                            {
                                "id": "90bcb083c07341a9bacbddffb5e5e39c",
                                "name": "OCR/Text Detection"
                            }
                        ],
                        "usedScene": [
                            {
                                "id": "3d1d13c6f01f4dceb17e8204b73a2d68",
                                "name": "Vehicle"
                            }
                        ]
                    }
                }
            ],
            "offset": 0,
            "recordSize": 2,
            "totalCount": 2
        }

        Get the dataset with the given dataset name:
        List datasets:

        >>> list_datasets(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     name="OxfordIIITPet"
        ... )
        {
            "datasets": [
                {
                    "id": "2bc95d506db2401b898067f1045d7f68",
                    "name": "OxfordIIITPet",
                    "alias": "Oxford-IIIT Pet",
                    "type": 0,
                    "defaultBranch": "main",
                    "commitId": "a0d4065872f245e4ad1d0d1186e3d397",
                    "coverUrl": "https://tutu.s3.cn-northwest-1.amazonaws.com.cn/
                        openDatasetImages_new_V4/OxfordIIITPet/cover-OxfordIIITPet.jpg",
                    "dataCount": 7390,
                    "dataSize": 791309002,
                    "updateTime": 1643015490,
                    "owner": "czhual",
                    "tabs": {
                        "dataType": [
                            {
                                "id": "69fe9a0fd4da42f9bf2ce4cd8ece8cbc",
                                "name": "Image"
                            }
                        ],
                        "labelType": [
                            {
                                "id": "5afe36dbefe74801a0ed264b438c0c9b",
                                "name": "Box2D"
                            },
                            {
                                "id": "9c156d3aa81646d18946873de5f2db20",
                                "name": "Classification"
                            },
                            {
                                "id": "c21ba730553d4729a9411a0843e2bcde",
                                "name": "SemanticMask"
                            }
                        ],
                        "usedScene": [
                            {
                                "id": "83aff47fcde14ae5a67ea12950333b71",
                                "name": "Animal"
                            }
                        ]
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
    url = urljoin(url, f"{PARTIAL_URL}/datasets")
    params: Dict[str, Any] = {"offset": offset, "limit": limit}
    if name:
        params["name"] = name

    return open_api_do(url, access_key, "GET", params=params).json()  # type: ignore[no-any-return]


def get_total_size(
    url: str,
    access_key: str,
    dataset_id: str,
    commit: str,
) -> Dict[str, int]:
    """Execute the OpenAPI `GET /v1/datasets{id}/total-size`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        commit: The information to locate the specific commit, which can be the commit id,
            the branch name, or the tag name.

    Examples:
        Get the total size of the dataset with the given id and commit:

        >>> get_total_size(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     "main"
        ... )
        {
            "totalSize": 791309002
        }

    Returns:
        The response of OpenAPI.

    """
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}/total-size")
    params = {"commit": commit}
    return open_api_do(url, access_key, "GET", params=params).json()  # type: ignore[no-any-return]
