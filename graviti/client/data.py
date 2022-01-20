#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#

"""Interfaces about data."""

from typing import Any, Dict, Optional
from urllib.parse import urljoin

from graviti.client.request import PARTIAL_URL, open_api_do


def list_data(
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

    Examples:
        List data of the segment with the given name and commit/draft_number:

        >>> list_data(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     "test",
        ...     commit="main"
        ... )
        {
            "segmentName": "test",
            "type": 0,
            "data": [
                {
                    "remotePath": "Abyssinian_002.jpg",
                    "checksum": "abd792a155306e9cd95c04453585bc935f8e035a"
                },
                {
                    "remotePath": "Abyssinian_003.jpg",
                    "checksum": "aa2b8272c79307b070a323786156888fade039fb"
                },
                {
                    "remotePath": "Abyssinian_004.jpg",
                    "checksum": "45dd8bab98187d89b3857b13a3843207eb7e4df6"
                },
                {
                    "remotePath": "Abyssinian_005.jpg",
                    "checksum": "b104c78b54a8113e62a3a4f0e8017d36fc7849c9"
                },
                ...
            ],
            "offset": 0,
            "recordSize": 128,
            "totalCount": 3704
        }

    Returns:
        The response of OpenAPI.

    """
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}/data")
    params: Dict[str, Any] = {"segmentName": segment_name, "offset": offset, "limit": limit}

    if draft_number:
        params["draftNumber"] = draft_number
    if commit:
        params["commit"] = commit

    return open_api_do(url, access_key, "GET", params=params).json()  # type: ignore[no-any-return]


def list_data_details(
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

    Examples:
        List data details of the segment with the given name and commit/draft_number:

        >>> list_data_details(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     "test",
        ...     commit="main"
        ... )
        {
            "segmentName": "test",
            "type": 0,
            "dataDetails": [
                {
                    "remotePath": "Abyssinian_002.jpg",
                    "checksum": "abd792a155306e9cd95c04453585bc935f8e035a",
                    "url": "https://pro-dataplatform-version.s3-accelerate.amazonaws.com/
                        460dcf7bf0e6814287c3190ddaa589b80045efec?X-Amz-Algorithm=AWS4-HMAC-SHA256&X
                        -Amz-Credential=AKIAQHTWCA3JFQMBFK5T%2F20220124%2Fus-west-1%2Fs3%2Faws4
                        _request&X-Amz-Date=20220124T113435Z&X-Amz-Expires=86400&X-Amz-SignedHeaders
                        =host&X-Amz-Signature=8ca0815037ef11effdc589983bb07f738fd7f3a0ec8b902dbf0ea
                        a5861340450",
                    "label": {
                        "CLASSIFICATION": {
                            "category": "Cat.Abyssinian"
                        },
                        "SEMANTIC_MASK": {
                            "checksum": "997a137a5915963a93cd2da318013927dbfc1632",
                            "remotePath": "Abyssinian_002.png",
                            "url": "https://pro-dataplatform-version.s3-accelerate.amazonaws.com/
                                997a137a5915963a93cd2da318013927dbfc1632?X-Amz-Algorithm=AWS4-HMAC
                                -SHA256&X-Amz-Credential=AKIAQHTWCA3JFQMBFK5T%2F20220124%2Fus-west
                                -1%2Fs3%2Faws4_request&X-Amz-Date=20220124T113435Z&X-Amz-Expires=
                                86400&X-Amz-SignedHeaders=host&X-Amz-Signature=
                                c888dfaf8eca42b3c693f1e372252541c35c8a197b72f03ffbc2bf2e7249fdc3"
                        }
                    }
                },
                {
                    "remotePath": "Abyssinian_003.jpg",
                    "checksum": "aa2b8272c79307b070a323786156888fade039fb",
                    "url": "https://pro-dataplatform-version.s3-accelerate.amazonaws.com/
                        49f003b21b8ae4f3ff2f74f13f2e99cefdec999d?X-Amz-Algorithm=AWS4-HMAC-SHA256&X
                        -Amz-Credential=AKIAQHTWCA3JFQMBFK5T%2F20220124%2Fus-west-1%2Fs3%2Faws4
                        _request&X-Amz-Date=20220124T113435Z&X-Amz-Expires=86400&X-Amz-SignedHeader
                        s=host&X-Amz-Signature=ae4399c1302896aeb8d03602b514e02f24b234c4ce212d15c003
                        d4cdd03e16b7",
                    "label": {
                        "CLASSIFICATION": {
                            "category": "Cat.Abyssinian"
                        },
                        "SEMANTIC_MASK": {
                            "checksum": "0702933b25e409e78d256b705aa13e9abede571e",
                            "remotePath": "Abyssinian_003.png",
                            "url": "https://pro-dataplatform-version.s3-accelerate.amazonaws.com/
                                0702933b25e409e78d256b705aa13e9abede571e?X-Amz-Algorithm=AWS4-HMAC
                                -SHA256&X-Amz-Credential=AKIAQHTWCA3JFQMBFK5T%2F20220124%2Fus-west
                                -1%2Fs3%2Faws4_request&X-Amz-Date=20220124T113435Z&X-Amz-Expires
                                =86400&X-Amz-SignedHeaders=host&X-Amz-Signature=6de16cb733a72c40ac
                                47da7565c6c73c033c501f3cd3927276eaa707dae34f5a"
                        }
                    }
                },
                ...
            ],
            "offset": 0,
            "recordSize": 128,
            "totalCount": 3704
        }

        Get data details with the given segment name, remote path and commit/draft_number:

        >>> list_data_details(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     "test",
        ...     commit="main",
        ...     remote_path="Abyssinian_003.jpg"
        ... )
        {
            "segmentName": "test",
            "type": 0,
            "dataDetails": [
                {
                    "remotePath": "Abyssinian_003.jpg",
                    "checksum": "aa2b8272c79307b070a323786156888fade039fb",
                    "url": "https://pro-dataplatform-version.s3-accelerate.amazonaws.com/
                        49f003b21b8ae4f3ff2f74f13f2e99cefdec999d?X-Amz-Algorithm=AWS4-HMAC-
                        SHA256&X-Amz-Credential=AKIAQHTWCA3JFQMBFK5T%2F20220124%2Fus-west-1%2Fs3%
                        2Faws4_request&X-Amz-Date=20220124T114154Z&X-Amz-Expires=86400&X-Amz-
                        SignedHeaders=host&X-Amz-Signature=8c91239ef9434a8b9bd62bb0f9757f846de56c
                        650a0ddb87b9745bca1bcd1ccf",
                    "label": {
                        "CLASSIFICATION": {
                            "category": "Cat.Abyssinian"
                        },
                        "SEMANTIC_MASK": {
                            "checksum": "0702933b25e409e78d256b705aa13e9abede571e",
                            "remotePath": "Abyssinian_003.png",
                            "url": "https://pro-dataplatform-version.s3-accelerate.amazonaws.com/
                                0702933b25e409e78d256b705aa13e9abede571e?X-Amz-Algorithm=AWS4-HMAC-
                                SHA256&X-Amz-Credential=AKIAQHTWCA3JFQMBFK5T%2F20220124%2Fus-west-
                                1%2Fs3%2Faws4_request&X-Amz-Date=20220124T114154Z&X-Amz-Expires=
                                86400&X-Amz-SignedHeaders=host&X-Amz-Signature=c0d15a972e3b5318e
                                66af924195fd61741426a4f3b7fd29093ec7b1699b162f8"
                        }
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
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}/data/details")
    params: Dict[str, Any] = {"segmentName": segment_name, "offset": offset, "limit": limit}

    if draft_number:
        params["draftNumber"] = draft_number
    if commit:
        params["commit"] = commit
    if remote_path:
        params["remotePath"] = remote_path
    if is_internal:
        params["isInternal"] = is_internal

    return open_api_do(url, access_key, "GET", params=params).json()  # type: ignore[no-any-return]


def list_data_urls(
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

    Examples:
        List data urls of the segment with the given name and commit/draft_number:

        >>> list_data_urls(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     "test",
        ...     commit="main"
        ... )
        {
            "segmentName": "test",
            "urls": [
                {
                    "remotePath": "Abyssinian_002.jpg",
                    "url": "https://pro-dataplatform-version.s3-accelerate.amazonaws.com/
                        460dcf7bf0e6814287c3190ddaa589b80045efec?X-Amz-Algorithm=AWS4-HMAC-SHA256&
                        X-Amz-Credential=AKIAQHTWCA3JFQMBFK5T%2F20220124%2Fus-west-1%2Fs3%2Faws4_
                        request&X-Amz-Date=20220124T114451Z&X-Amz-Expires=86400&X-Amz-SignedHeaders
                        =host&X-Amz-Signature=8180b432736b4f9f31a1880f136668ee0f52bc590c297620a05df
                        122b5cd3e73"
                },
                {
                    "remotePath": "Abyssinian_003.jpg",
                    "url": "https://pro-dataplatform-version.s3-accelerate.amazonaws.com/
                        49f003b21b8ae4f3ff2f74f13f2e99cefdec999d?X-Amz-Algorithm=AWS4-HMAC-SHA256&X
                        -Amz-Credential=AKIAQHTWCA3JFQMBFK5T%2F20220124%2Fus-west-1%2Fs3%2Faws4_
                        request&X-Amz-Date=20220124T114451Z&X-Amz-Expires=86400&X-Amz-
                        SignedHeaders=host&X-Amz-Signature=33a9da0cdf25688249c59fec6404
                        0bbc9ca462dbf8df920ee4a7eafa25ade7ee"
                },
                ...
            ],
            "offset": 0,
            "recordSize": 128,
            "totalCount": 3704
        }

        Get data urls with the given segment name, remote path and draft number or commit:

        >>> list_data_urls(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     "test",
        ...     commit="main",
        ...     remote_path="Abyssinian_003.jpg"
        ... )
        {
            "segmentName": "test",
            "urls": [
                {
                    "remotePath": "Abyssinian_003.jpg",
                    "url": "https://pro-dataplatform-version.s3-accelerate.amazonaws.com/
                        49f003b21b8ae4f3ff2f74f13f2e99cefdec999d?X-Amz-Algorithm=AWS4-HMAC-
                        SHA256&X-Amz-Credential=AKIAQHTWCA3JFQMBFK5T%2F20220124%2Fus-west-
                        1%2Fs3%2Faws4_request&X-Amz-Date=20220124T114745Z&X-Amz-Expires=86400&X-
                        Amz-SignedHeaders=host&X-Amz-Signature=5b0c279a61a53a3f9c7c9e5e0b5de6b3a
                        3811a4c1876a058b859ec744608940f"
                }
            ],
            "offset": 0,
            "recordSize": 0,
            "totalCount": 0
        }

    Returns:
        The response of OpenAPI.

    """
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}/data/urls")
    params: Dict[str, Any] = {"segmentName": segment_name, "offset": offset, "limit": limit}

    if draft_number:
        params["draftNumber"] = draft_number
    if commit:
        params["commit"] = commit
    if remote_path:
        params["remotePath"] = remote_path
    if is_internal:
        params["isInternal"] = is_internal

    return open_api_do(url, access_key, "GET", params=params).json()  # type: ignore[no-any-return]


def list_mask_urls(
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

    Examples:
        List mask urls of the segment with the given name and commit/draft_number:

        >>> list_mask_urls(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     "test",
        ...     "SEMANTIC_MASK",
        ...     commit="main"
        ... )
        {
            "segmentName": "test",
            "urls": [
                {
                    "remotePath": "Abyssinian_002.png",
                    "url": "https://pro-dataplatform-version.s3-accelerate.amazonaws.com/
                        997a137a5915963a93cd2da318013927dbfc1632?X-Amz-Algorithm=AWS4-HMAC-
                        SHA256&X-Amz-Credential=AKIAQHTWCA3JFQMBFK5T%2F20220124%2Fus-west-
                        1%2Fs3%2Faws4_request&X-Amz-Date=20220124T115625Z&X-Amz-Expires=
                        86400&X-Amz-SignedHeaders=host&X-Amz-Signature=95011ca650a5da6e2e
                        9077c425f878d4ba446f2f5032ab8622f72111816d43d4"
                },
                {
                    "remotePath": "Abyssinian_003.png",
                    "url": "https://pro-dataplatform-version.s3-accelerate.amazonaws.com/
                        0702933b25e409e78d256b705aa13e9abede571e?X-Amz-Algorithm=AWS4-HMAC-
                        SHA256&X-Amz-Credential=AKIAQHTWCA3JFQMBFK5T%2F20220124%2Fus-west-
                        1%2Fs3%2Faws4_request&X-Amz-Date=20220124T115625Z&X-Amz-Expires=86400&X-
                        Amz-SignedHeaders=host&X-Amz-Signature=c116ac8efcebaa34698350add2f
                        238fa3c53a5cd02ae3e605109e37c7efcc820"
                },
            ],
            "offset": 0,
            "recordSize": 128,
            "totalCount": 3704
        }

        Get mask urls with the given segment name, remote path and commit/draft_number:

        >>> list_mask_urls(
        ...     "https://gas.graviti.com/",
        ...     "ACCESSKEY-********",
        ...     "2bc95d506db2401b898067f1045d7f68",
        ...     "main",
        ...     "SEMANTIC_MASK",
        ...     commit="main",
        ...     remote_path="Abyssinian_003.png"
        ... )
        {
            "segmentName": "test",
            "urls": [
                {
                    "remotePath": "Abyssinian_003.png",
                    "url": "https://pro-dataplatform-version.s3-accelerate.amazonaws.com/
                        0702933b25e409e78d256b705aa13e9abede571e?X-Amz-Algorithm=AWS4-HMAC-
                        SHA256&X-Amz-Credential=AKIAQHTWCA3JFQMBFK5T%2F20220124%2Fus-west-
                        1%2Fs3%2Faws4_request&X-Amz-Date=20220124T115957Z&X-Amz-Expires=86400&X-
                        Amz-SignedHeaders=host&X-Amz-Signature=0709dc6e14f09ba79b7a346d901b70c
                        ab8ada3fa837c5eb54c7c88acda60959b"
                }
            ],
            "offset": 0,
            "recordSize": 1,
            "totalCount": 3704
        }

    Returns:
        The response of OpenAPI.

    """
    url = urljoin(url, f"{PARTIAL_URL}/datasets/{dataset_id}/masks/urls")
    params: Dict[str, Any] = {
        "segmentName": segment_name,
        "maskType": mask_type,
        "offset": offset,
        "limit": limit,
    }

    if draft_number:
        params["draftNumber"] = draft_number
    if commit:
        params["commit"] = commit
    if remote_path:
        params["remotePath"] = remote_path
    if is_internal:
        params["isInternal"] = is_internal

    return open_api_do(url, access_key, "GET", params=params).json()  # type: ignore[no-any-return]
