#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Deprecated classes referring to TensorBay exceptions. This file will be removed in v1.5.0.

GASDatasetTypeError and GASResponseError are deprecated since v1.3.0, and will be removed in v1.5.0.

Please use :class:`~tensorbay.exception.DatasetTypeError` instead of :class:`GASDatasetTypeError`.
Please use :class:`~tensorbay.exception.ResponseError` instead of :class:`GASResponseError`.

GASDatasetError, GASSegmentError and GASPathError are deprecated since v1.4.0,
and will be removed in v1.5.0.

Please use :class:`~tensorbay.exception.ResourceNotExistError`
instead of :class:`GASDatasetError` and :class:`GASSegmentError`.

Please use :class:`~tensorbay.exception.InvalidParamsError` instead of :class:`GASPathError`.

"""

from ..exception import (
    ClientError,
    DatasetTypeError,
    InvalidParamsError,
    ResourceNotExistError,
    ResponseError,
)

GASException = ClientError
GASDatasetTypeError = DatasetTypeError
GASResponseError = ResponseError
GASDatasetError = ResourceNotExistError
GASSegmentError = ResourceNotExistError
GASPathError = InvalidParamsError
