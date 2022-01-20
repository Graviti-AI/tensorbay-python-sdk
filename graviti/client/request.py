#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""The basic concepts and methods of the Graviti Open API."""

import logging
from typing import Any
from uuid import uuid4

from requests.models import Response

from tensorbay.__version__ import __version__
from tensorbay.exception import ResponseError, ResponseErrorDistributor
from tensorbay.utility import config, get_session

logger = logging.getLogger(__name__)
PARTIAL_URL = "gatewayv2/tensorbay-open-api/v1"


def open_api_do(url: str, access_key: str, method: str, **kwargs: Any) -> Response:
    """Send a request to the TensorBay Open API.

    Arguments:
        access_key: User's access key.
        method: The method of the request.
        url: The URL of the graviti website.
        **kwargs: Extra keyword arguments to send in the POST request.

    Raises:
        ResponseError: When the status code OpenAPI returns is unexpected.

    Returns:
        Response of the request.

    """
    headers = kwargs.setdefault("headers", {})
    headers["X-Token"] = access_key
    headers["X-Source"] = f"{config._x_source}/{__version__}"  # pylint: disable=protected-access
    headers["X-Request-Id"] = uuid4().hex

    try:
        return get_session().request(method=method, url=url, **kwargs)
    except ResponseError as error:
        response = error.response
        error_code = response.json()["code"]
        raise ResponseErrorDistributor.get(error_code, ResponseError)(response=response) from None
