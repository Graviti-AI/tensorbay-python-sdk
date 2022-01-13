#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""The basic concepts and methods of the Graviti Open API."""

import logging
from typing import Any

from requests.models import Response

logger = logging.getLogger(__name__)


def open_api_do(
    url: str, access_key: str, method: str, **kwargs: Any  # pylint: disable=unused-argument
) -> Response:
    """Send a request to the TensorBay Open API.

    Arguments:
        access_key: User's access key.
        method: The method of the request.
        url: The URL of the graviti website.
        **kwargs: Extra keyword arguments to send in the POST request.

    Raises:# flake8: noqa: F402
        ResponseError: When the status code OpenAPI returns is unexpected.

    Return:
        Response of the request.

    """
