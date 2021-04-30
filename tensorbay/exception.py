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
                 +-- AccessDeniedError
                 +-- InvalidParamsError
                 +-- NameConflictError
                 +-- RequestParamsMissingError
                 +-- ResourceNotExistError
                 +-- ResponseSystemError
                 +-- UnauthorizedError
         +-- TBRNError
         +-- TensorBayOpenDatasetError
             +-- NoFileError
             +-- FileStructureError

"""

from typing import Dict, Optional, Type, Union

from requests.models import Response


class TensorBayException(Exception):
    """This is the base class for TensorBay custom exceptions."""


class TensorBayClientError(TensorBayException):
    """This is the base class for custom exceptions in TensorBay client module."""


class CommitStatusError(TensorBayClientError):
    """This class defines the exception for illegal commit status.

    Arguments:
        is_draft: Whether the commit status is draft.

    """

    def __init__(self, is_draft: bool) -> None:
        super().__init__()
        self._required_status = "commit" if is_draft else "draft"

    def __str__(self) -> str:
        return f"The status is not {self._required_status}"


class DatasetTypeError(TensorBayClientError):
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


class FrameError(TensorBayClientError):
    """This class defines the exception for incorrect frame id.

    Arguments:
       message: The error message.

    """

    def __init__(self, message: str) -> None:
        super().__init__()
        self._message = message

    def __str__(self) -> str:
        return self._message


class ResponseError(TensorBayClientError):
    """This class defines the exception for post response error.

    Arguments:
        response: The response of the request.

    Attributes:
        response: The response of the request.

    """

    # https://github.com/python/mypy/issues/6473
    _INDENT = " " * len(__qualname__)  # type: ignore[name-defined]

    STATUS_CODE: int

    def __init__(self, response: Response) -> None:
        super().__init__()
        self.response = response

    def __init_subclass__(cls) -> None:
        cls._INDENT = " " * len(cls.__name__)

    def __str__(self) -> str:
        return (
            f"Unexpected status code({self.response.status_code})! {self.response.url}!"
            f"\n{self._INDENT}  {self.response.json()['message']}"
        )


class AccessDeniedError(ResponseError):
    """This class defines the exception for access denied response error."""

    STATUS_CODE = 403


class InvalidParamsError(ResponseError):
    """This class defines the exception for invalid parameters response error.

    Arguments:
        response: The response of the request.
        param_name: The name of the invalid parameter.
        param_value: The value of the invalid parameter.

    Attributes:
        response: The response of the request.

    """

    STATUS_CODE = 400

    def __init__(  # pylint: disable=super-init-not-called
        self,
        response: Optional[Response] = None,
        *,
        param_name: Optional[str] = None,
        param_value: Optional[str] = None,
    ) -> None:
        if response is not None:
            super().__init__(response)
            return

        self._param_name = param_name
        self._param_value = param_value

    def __str__(self) -> str:
        if hasattr(self, "response"):
            return super().__str__()

        messages = [f"Invalid {self._param_name}: {self._param_value}."]
        if self._param_name == "path":
            messages.append("Remote path should follow linux style.")

        return f"\n{self._INDENT}".join(messages)


class NameConflictError(ResponseError):
    """This class defines the exception for name conflict response error.

    Arguments:
        response: The response of the request.
        resource: The type of the conflict resource.
        identification: The identification of the conflict resource.

    Attributes:
        response: The response of the request.

    """

    STATUS_CODE = 400

    def __init__(  # pylint: disable=super-init-not-called
        self,
        response: Optional[Response] = None,
        *,
        resource: Optional[str] = None,
        identification: Union[int, str, None] = None,
    ) -> None:
        if response is not None:
            super().__init__(response)
            return

        self._resource = resource
        self._identification = identification

    def __str__(self) -> str:
        if hasattr(self, "response"):
            return super().__str__()

        return f"The {self._resource}: {self._identification} already exists."


class RequestParamsMissingError(ResponseError):
    """This class defines the exception for request parameters missing response error."""

    STATUS_CODE = 400


class ResourceNotExistError(ResponseError):
    """This class defines the exception for resource not existing response error.

    Arguments:
        response: The response of the request.
        resource: The type of the conflict resource.
        identification: The identification of the conflict resource.

    Arguments:
        response: The response of the request.

    """

    STATUS_CODE = 404

    def __init__(  # pylint: disable=super-init-not-called
        self,
        response: Optional[Response] = None,
        *,
        resource: Optional[str] = None,
        identification: Union[int, str, None] = None,
    ) -> None:
        if response is not None:
            super().__init__(response)
            return

        self._resource = resource
        self._identification = identification

    def __str__(self) -> str:
        if hasattr(self, "response"):
            return super().__str__()

        return f"The {self._resource}: {self._identification} does not exist."


class ResponseSystemError(ResponseError):
    """This class defines the exception for system response error."""

    STATUS_CODE = 500


class UnauthorizedError(ResponseError):
    """This class defines the exception for unauthorized response error."""

    STATUS_CODE = 401


class TensorBayOpendatasetError(TensorBayException):
    """This is the base class for custom exceptions in TensorBay opendataset module."""


class NoFileError(TensorBayOpendatasetError):
    """This class defines the exception for no matching file found in the opendataset directory.

    Arguments:
        pattern: Glob pattern.

    """

    def __init__(self, pattern: str) -> None:
        super().__init__()
        self._pattern = pattern

    def __str__(self) -> str:
        return f'No file follows the giving pattern "{self._pattern}"'


class FileStructureError(TensorBayOpendatasetError):
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


ResponseErrorDistributor: Dict[str, Type[ResponseError]] = {
    "AccessDenied": AccessDeniedError,
    "InvalidParamsValue": InvalidParamsError,
    "NameConflict": NameConflictError,
    "RequestParamsMissing": RequestParamsMissingError,
    "ResourceNotExist": ResourceNotExistError,
    "SystemError": ResponseSystemError,
    "Unauthorized": UnauthorizedError,
}
