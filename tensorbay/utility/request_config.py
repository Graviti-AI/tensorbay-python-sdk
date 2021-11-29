#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""The request related configs."""


class Config:
    """This is a base class defining the concept of Request Config.

    Attributes:
        max_retries: Maximum retry times of the request.
        allowed_retry_methods: The allowed methods for retrying request.
        allowed_retry_status: The allowed status for retrying request.
            If both methods and status are fitted, the retrying strategy will work.
        timeout: Timeout value of the request in seconds.
        is_internal: Whether the request is from internal.

    """

    def __init__(self) -> None:

        self.max_retries = 3
        self.allowed_retry_methods = ["HEAD", "OPTIONS", "POST", "PUT"]
        self.allowed_retry_status = [429, 500, 502, 503, 504]

        self.timeout = 30
        self.is_internal = False
        self._x_source = "PYTHON-SDK"


config = Config()
