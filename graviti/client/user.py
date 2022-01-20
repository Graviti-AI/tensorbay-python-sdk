#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Interfaces about the user."""

from typing import Any, Dict
from urllib.parse import urljoin

from graviti.client.request import PARTIAL_URL, open_api_do


def get_user(url: str, access_key: str) -> Dict[str, Any]:  # pylint: disable=unused-argument
    """Execute the OpenAPI `GET /v1/users`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.

    Returns:
        The response of OpenAPI.

    Examples:
        Get information of user with the given access_key:

        >>> get_user("https://gas.graviti.com/", "ACCESSKEY-********")
        {
            "id": "41438e9df9a82a194e1e76cc31c1d8d4",
            "nickname": "czhual",
            "email": "********@graviti.com",
            "mobile": null,
            "description": "",
            "team": null
        }

    """
    url = urljoin(url, f"{PARTIAL_URL}/users")
    return open_api_do(url, access_key, "GET").json()  # type: ignore[no-any-return]
