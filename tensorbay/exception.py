#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""TensorBay cutoms exceptions.

The class hierarchy for TensorBay custom exceptions is::

     +-- TensorBayException
         +-- ClientError
             +-- StatusError
             +-- DatasetTypeError
             +-- FrameError
             +-- ResponseError
                 +-- AccessDeniedError
                 +-- ForbiddenError
                 +-- InvalidParamsError
                 +-- NameConflictError
                 +-- RequestParamsMissingError
                 +-- ResourceNotExistError
                 +-- InternalServerError
                 +-- UnauthorizedError
        +-- UtilityError
            +-- AttrError
         +-- TBRNError
         +-- OpenDatasetError
             +-- NoFileError
             +-- FileStructureError

:class:`ResponseSystemError` is deprecated since version v1.11.0.
It will be removed in version v1.13.0. Use :class:`InternalServerError` instead.

"""

from typing import Dict, Optional, Type, Union

from requests.models import Response


class TensorBayException(Exception):
    """This is the base class for TensorBay custom exceptions.

    Arguments:
       message: The error message.

    """

    def __init__(self, message: Optional[str] = None):
        super().__init__()
        self._message = message

    def __str__(self) -> str:
        return self._message if self._message else ""


class ClientError(TensorBayException):
    """This is the base class for custom exceptions in TensorBay client module."""


class StatusError(ClientError):
    """This class defines the exception for illegal status.

    Arguments:
        is_draft: Whether the status is draft.
        message: The error message.

    """

    def __init__(self, message: Optional[str] = None, *, is_draft: Optional[bool] = None) -> None:
        super().__init__()
        if is_draft is None:
            self._message = message
        else:
            required_status = "commit" if is_draft else "draft"
            self._message = f"The status is not {required_status}"


class DatasetTypeError(ClientError):
    """This class defines the exception for incorrect type of the requested dataset.

    Arguments:
        dataset_name: The name of the dataset whose requested type is wrong.
        is_fusion: Whether the dataset is a fusion dataset.

    """

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        dataset_name: Optional[str] = None,
        is_fusion: Optional[bool] = None,
    ) -> None:
        super().__init__(message)
        self._dataset_name = dataset_name
        self._is_fusion = is_fusion

    def __str__(self) -> str:
        if self._dataset_name and self._is_fusion:
            return f'Dataset "{self._dataset_name}" is \
            {"" if self._is_fusion else "not "}a fusion dataset'
        return super().__str__()


class FrameError(ClientError):
    """This class defines the exception for incorrect frame id."""


class OperationError(ClientError):
    """This class defines the exception for incorrect operation."""


class ResponseError(ClientError):
    """This class defines the exception for post response error.

    Arguments:
        response: The response of the request.

    Attributes:
        response: The response of the request.

    """

    # https://github.com/python/mypy/issues/6473
    _INDENT = " " * len(__qualname__)  # type: ignore[name-defined]

    STATUS_CODE: int

    def __init__(
        self, message: Optional[str] = None, *, response: Optional[Response] = None
    ) -> None:
        super().__init__(message)
        if response is not None:
            self.response = response

    def __init_subclass__(cls) -> None:
        cls._INDENT = " " * len(cls.__name__)

    def __str__(self) -> str:
        if hasattr(self, "response"):
            return (
                f"Unexpected status code({self.response.status_code})! {self.response.url}!"
                f"\n{self._INDENT}  {self.response.text}"
            )
        return super().__str__()


class AccessDeniedError(ResponseError):
    """This class defines the exception for access denied response error."""

    STATUS_CODE = 403


class ForbiddenError(ResponseError):
    """This class defines the exception for illegal operations Tensorbay forbids."""

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
        message: Optional[str] = None,
        *,
        response: Optional[Response] = None,
        param_name: Optional[str] = None,
        param_value: Optional[str] = None,
    ) -> None:
        super().__init__(message, response=response)
        self._param_name = param_name
        self._param_value = param_value

    def __str__(self) -> str:
        if self._param_name and self._param_value:
            messages = [f"Invalid {self._param_name}: {self._param_value}."]
            if self._param_name == "path":
                messages.append("Remote path should follow linux style.")

            return f"\n{self._INDENT}".join(messages)
        return super().__str__()


class NameConflictError(ResponseError):
    """This class defines the exception for name conflict response error.

    Arguments:
        response: The response of the request.
        resource: The type of the conflict resource.
        identification: The identification of the conflict resource.

    Attributes:
        response: The response of the request.

    """

    STATUS_CODE = 409

    def __init__(  # pylint: disable=super-init-not-called
        self,
        message: Optional[str] = None,
        *,
        response: Optional[Response] = None,
        resource: Optional[str] = None,
        identification: Union[int, str, None] = None,
    ) -> None:
        super().__init__(message, response=response)
        self._resource = resource
        self._identification = identification

    def __str__(self) -> str:
        if self._resource and self._identification:
            return f"The {self._resource}: {self._identification} already exists."
        return super().__str__()


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
        message: Optional[str] = None,
        *,
        response: Optional[Response] = None,
        resource: Optional[str] = None,
        identification: Union[int, str, None] = None,
    ) -> None:
        super().__init__(message, response=response)
        self._resource = resource
        self._identification = identification

    def __str__(self) -> str:
        if self._resource and self._identification:
            return f"The {self._resource}: {self._identification} does not exist."
        return super().__str__()


class InternalServerError(ResponseError):
    """This class defines the exception for internal server error."""

    STATUS_CODE = 500


ResponseSystemError = InternalServerError


class UnauthorizedError(ResponseError):
    """This class defines the exception for unauthorized response error."""

    STATUS_CODE = 401


class OpenDatasetError(TensorBayException):
    """This is the base class for custom exceptions in TensorBay opendataset module."""


class NoFileError(OpenDatasetError):
    """This class defines the exception for no matching file found in the opendataset directory.

    Arguments:
        pattern: Glob pattern.

    """

    def __init__(self, message: Optional[str] = None, *, pattern: Optional[str] = None) -> None:
        super().__init__(message)
        self._pattern = pattern

    def __str__(self) -> str:
        if self._pattern:
            return f'No file follows the giving pattern "{self._pattern}"'
        return super().__str__()


class FileStructureError(OpenDatasetError):
    """This class defines the exception for incorrect file structure in opendataset directory."""


class ModuleImportError(OpenDatasetError, ModuleNotFoundError):
    """This class defines the exception for import error of optional module in opendataset module.

    Arguments:
        module_name: The name of the optional module.
        package_name: The package name of the optional module.

    """

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        module_name: Optional[str] = None,
        package_name: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self._module_name = module_name
        self._package_name = package_name if package_name else module_name

    def __str__(self) -> str:
        if self._module_name:
            return (
                f"No module named {self._module_name}."
                "\n"
                f'\n    To install the module, please run: "pip3 install {self._package_name}"'
                "\n"
            )
        return super().__str__()


class TBRNError(TensorBayException):
    """This class defines the exception for invalid TBRN."""


ResponseErrorDistributor: Dict[str, Type[ResponseError]] = {
    "AccessDenied": AccessDeniedError,
    "Forbidden": ForbiddenError,
    "InvalidParamsValue": InvalidParamsError,
    "NameConflict": NameConflictError,
    "RequestParamsMissing": RequestParamsMissingError,
    "ResourceNotExist": ResourceNotExistError,
    "InternalServerError": InternalServerError,
    "Unauthorized": UnauthorizedError,
}


class UtilityError(TensorBayException):
    """This is the base class for custom exceptions in TensorBay utility module."""


class AttrError(UtilityError):
    """This class defines the exception for dynamic attr have default value."""

    def __str__(self) -> str:
        return "Dynamic attr cannot have default value."
