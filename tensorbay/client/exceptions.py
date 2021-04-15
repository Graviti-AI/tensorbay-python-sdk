#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Classes refer to TensorBay exceptions.

+----------------------+-----------------------------------------------------+
| Error                | Description                                         |
+======================+=====================================================+
| GASDatasetError      | The requested dataset does not exist                |
+----------------------+-----------------------------------------------------+
| GASSegmentError      | The requested segment does not exist                |
+----------------------+-----------------------------------------------------+
| GASPathError         | Remote path does not follow linux style             |
+----------------------+-----------------------------------------------------+

GASDatasetTypeError and GASResponseError are deprecated since v1.3.0, and will be removed in v1.5.0.

Please use :class:`~tensorbay.exception.DatasetTypeError` instead of :class:`GASDatasetTypeError`.
Please use :class:`~tensorbay.exception.ResponseError` instead of :class:`GASResponseError`.

"""

from ..exception import DatasetTypeError, ResponseError, TensorBayClientException

GASException = TensorBayClientException
GASDatasetTypeError = DatasetTypeError
GASResponseError = ResponseError


class GASDatasetError(GASException):
    """This error is raised to indicate that the requested dataset does not exist.

    Arguments:
        dataset_name: The name of the missing dataset.

    """

    def __init__(self, dataset_name: str) -> None:
        super().__init__()
        self._dataset_name = dataset_name

    def __str__(self) -> str:
        return f"Dataset '{self._dataset_name}' does not exist"


class GASSegmentError(GASException):
    """This error is raised to indicate that the requested segment does not exist.

    Arguments:
        segment_name: The name of the missing segment_name.

    """

    def __init__(self, segment_name: str) -> None:
        super().__init__()
        self._segment_name = segment_name

    def __str__(self) -> str:
        return f"Segment '{self._segment_name}' does not exist"


class GASPathError(GASException):
    """This error is raised to indicate that remote path does not follow linux style.

    Arguments:
        remote_path: The invalid remote path.

    """

    def __init__(self, remote_path: str) -> None:
        super().__init__()
        self._remote_path = remote_path

    def __str__(self) -> str:
        return f'Invalid path: "{self._remote_path}"\nRemote path should follow linux style.'
