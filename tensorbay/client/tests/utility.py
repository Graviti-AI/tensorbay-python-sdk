#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Utility method for unit test in client module."""

from typing import Any

from mock import Mock


def mock_response(status: int = 200, content: str = "CONTENT", data: Any = None) -> Any:
    """A helper function to mock a responses with the given arguments.

    Arguments:
        status: status code of response.
        content: content value of response.
        data: The return value of response.

    Returns:
        Mocker of the response.
    """
    mock_resp = Mock()
    mock_resp.status_code = status
    mock_resp.content = content
    if data:
        mock_resp.json = Mock(return_value=data)
    return mock_resp
