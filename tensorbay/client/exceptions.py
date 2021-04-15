#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Classes refer to TensorBay exceptions.

+----------------------+-----------------------------------------------------+
| Error                | Description                                         |
+======================+=====================================================+
| GASResponseError     | Post response error                                 |
+----------------------+-----------------------------------------------------+
| GASDatasetError      | The requested dataset does not exist                |
+----------------------+-----------------------------------------------------+
| GASDatasetTypeError  | The type of the requested dataset is wrong          |
+----------------------+-----------------------------------------------------+
| GASSegmentError      | The requested segment does not exist                |
+----------------------+-----------------------------------------------------+
| GASPathError         | Remote path does not follow linux style             |
+----------------------+-----------------------------------------------------+

"""

from requests.models import Response


class GASException(Exception):
    """This defines the parent class to the following specified error classes."""


class GASResponseError(GASException):
    """This error is raised to indicate post response error.

    Arguments:
        response: The response of the request.

    """

    def __init__(self, response: Response) -> None:
        super().__init__()
        self.response = response
        self.status_code = response.status_code

    def __str__(self) -> str:
        return f"Invalid state code({self.status_code})! {self.response.url}"


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


class GASDatasetTypeError(GASException):
    """This error is raised to indicate that the type of the requested dataset is wrong.

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
