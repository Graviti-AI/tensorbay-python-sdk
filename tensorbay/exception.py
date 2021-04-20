#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""TensorBay cutoms exceptions.

The class hierarchy for TensorBay custom exceptions is::

     +-- TensorBayException
         +-- TensorBayClientError
             +-- CommitStatusError
             +-- DatasetTypeError
             +-- FrameError
             +-- ResponseError
         +-- TBRNError
         +-- TensorBayOpenDatasetError
             +-- NoFileError
             +-- FileStructureError

"""

from requests.models import Response


class TensorBayException(Exception):
    """This is the base class for TensorBay custom exceptions."""


class TensorBayClientException(TensorBayException):
    """This is the base class for custom exceptions in TensorBay client module."""


class CommitStatusError(TensorBayClientException):
    """This class defines the exception for illegal commit status.

    Arguments:
        is_draft: Whether the commit status is draft.

    """

    def __init__(self, is_draft: bool) -> None:
        super().__init__()
        self._required_status = "commit" if is_draft else "draft"

    def __str__(self) -> str:
        return f"The status is not {self._required_status}"


class DatasetTypeError(TensorBayClientException):
    """This class defines the exception for incorrect type of the requested dataset.

    Arguments:
        dataset_name: The name of the dataset whose requested type is wrong.
        is_fusion: Whether the dataset is a fusion dataset.

    """

    def __init__(self, dataset_name: str, is_fusion: bool) -> None:
        super().__init__()
        self._dataset_name = dataset_name
        self._is_fusion = is_fusion

    def __str__(self) -> str:
        return (
            f"Dataset '{self._dataset_name}' is {'' if self._is_fusion else 'not '}a fusion dataset"
        )


class FrameError(TensorBayClientException):
    """This class defines the exception for incorrect frame id.

    Arguments:
       message: The error message.

    """

    def __init__(self, message: str) -> None:
        super().__init__()
        self._message = message

    def __str__(self) -> str:
        return self._message


class ResponseError(TensorBayClientException):
    """This class defines the exception for post response error.

    Arguments:
        response: The response of the request.

    """

    def __init__(self, response: Response) -> None:
        super().__init__()
        self.response = response

    def __str__(self) -> str:
        return f"Unexpected status code({self.response.status_code})! {self.response.url}"


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


class TBRNError(TensorBayException):
    """This class defines the exception for invalid TBRN.

    Arguments:
        message: The error message.

    """

    def __init__(self, message: str) -> None:
        super().__init__()
        self._message = message

    def __str__(self) -> str:
        return self._message
