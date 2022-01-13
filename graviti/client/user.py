#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Interfaces about the user."""

from typing import Any, Dict


def get_user(url: str, access_key: str) -> Dict[str, Any]:  # pylint: disable=unused-argument
    """Execute the OpenAPI `GET /v1/users`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.

    Return:
        The response of OpenAPI.

    """
