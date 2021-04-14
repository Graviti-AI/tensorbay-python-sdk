#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""TensorBay cutoms exceptions.

The class hierarchy for TensorBay custom exceptions is::

     +-- :class:`TensorBayException`
         +-- :class:`TensorBayOpenDatasetError`
             +-- :class:`NoFileError`
             +-- :class:`FileStructureError`

"""


class TensorBayException(Exception):
    """This is the base class for TensorBay custom exceptions."""


class TensorBayOpendatasetException(TensorBayException):
    """This is the base class for custom exceptions in TensorBay opendataset module."""


class NoFileError(TensorBayOpendatasetException):
    """This class defines the exception for no matching file found in the opendataset directory.

    Arguments:
        pattern: Glob pattern.

    """

    def __init__(self, pattern: str) -> None:
        super().__init__()
        self._pattern = pattern

    def __str__(self) -> str:
        return f'No file follows the giving pattern "{self._pattern}"'


class FileStructureError(TensorBayOpendatasetException):
    """This class defines the exception for incorrect file structure in the opendataset directory.

    Arguments:
        message: The error message.

    """

    def __init__(self, message: str) -> None:
        super().__init__()
        self._message = message

    def __str__(self) -> str:
        return self._message
