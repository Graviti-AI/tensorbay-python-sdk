#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Exceptions about open data loader."""


class OpenDatasetException(Exception):
    """This is the parent class to all open dataset exceptions."""


class OpenDatasetNoFileError(OpenDatasetException):
    """Exception for no file found in the opendataset directory.

    Arguments:
        pattern: Glob pattern.

    """

    def __init__(self, pattern: str) -> None:
        super().__init__()
        self._pattern = pattern

    def __str__(self) -> str:
        return f'No file follows the giving pattern "{self._pattern}"'
