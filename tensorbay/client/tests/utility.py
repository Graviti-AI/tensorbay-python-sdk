#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Utility method for unit test in client module."""

from typing import Any, Callable, Optional
from unittest.mock import Mock


def mock_response(
    status: int = 200,
    content: str = "CONTENT",
    data: Any = None,
    read: Optional[Callable[[Any], Any]] = None,
) -> Mock:
    """A helper function to mock a responses with the given arguments.

    Arguments:
        status: Status code of response.
        content: Content value of response.
        data: The return value of response.
        read: The read function of the response.

    Returns:
        Mocker of the response.
    """
    response = Mock()
    response.status_code = status
    response.content = content
    if data:
        response.json = Mock(return_value=data)
    if read:
        response.read = read
        response.__enter__ = lambda *args: response
        response.__exit__ = lambda *args: None
    return response
