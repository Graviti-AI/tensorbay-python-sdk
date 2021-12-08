#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""The implementation of the TensorBay data."""

import os
from typing import Any, Dict, Optional, Type, TypeVar, Union

from tensorbay.label import Label
from tensorbay.utility import URL, FileMixin, RemoteFileMixin, ReprMixin


class DataBase(ReprMixin):
    """DataBase is a base class for the file and label combination.

    Arguments:
        timestamp: The timestamp for the file.

    Attributes:
        timestamp: The timestamp for the file.
        label: The :class:`~tensorbay.label.label.Label` instance that contains
            all the label information of the file.

    """

    _Type = Union["Data", "RemoteData", "AuthData"]

    _repr_attrs = ("timestamp", "label")

    def __init__(self, timestamp: Optional[float] = None) -> None:
        if timestamp is not None:
            self.timestamp = timestamp

        self.label = Label()


class Data(DataBase, FileMixin):
    """Data is a combination of a specific local file and its label.

    It contains the file local path, label information of the file
    and the file metadata, such as timestamp.

    A Data instance contains one or several types of labels.

    Arguments:
        local_path: The file local path.
        target_remote_path: The file remote path after uploading to tensorbay.
        timestamp: The timestamp for the file.

    Attributes:
        path: The file local path.
        timestamp: The timestamp for the file.
        label: The :class:`~tensorbay.label.label.Label` instance that contains
                all the label information of the file.
        target_remote_path: The target remote path of the data.

    """

    def __init__(
        self,
        local_path: str,
        *,
        target_remote_path: Optional[str] = None,
        timestamp: Optional[float] = None,
    ) -> None:
        DataBase.__init__(self, timestamp)
        FileMixin.__init__(self, local_path)
        self._target_remote_path = target_remote_path

    @property
    def target_remote_path(self) -> str:
        """Return the target remote path of the data.

        Target remote path will be used when this data is uploaded to tensorbay, and the target
        remote path will be the uploaded file's remote path.

        Returns:
            The target remote path of the data.

        """
        if not self._target_remote_path:
            self._target_remote_path = os.path.basename(self.path)

        return self._target_remote_path

    @target_remote_path.setter
    def target_remote_path(self, target_remote_path: str) -> None:
        self._target_remote_path = target_remote_path

    def get_callback_body(self) -> Dict[str, Any]:
        """Get the callback request body for uploading.

        Returns:
            The callback request body, which look like::

                    {
                        "remotePath": <str>,
                        "timestamp": <float>,
                        "checksum": <str>,
                        "fileSize": <int>,
                        "label": {
                            "CLASSIFICATION": {...},
                            "BOX2D": {...},
                            "BOX3D": {...},
                            "POLYGON": {...},
                            "POLYLINE2D": {...},
                            "KEYPOINTS2D": {...},
                            "SENTENCE": {...}
                        }
                    }

        """
        body = super()._get_callback_body()
        body["remotePath"] = self.target_remote_path
        if hasattr(self, "timestamp"):
            body["timestamp"] = self.timestamp
        if self.label:
            body["label"] = self.label.dumps()

        return body


class RemoteData(DataBase, RemoteFileMixin):
    """RemoteData is a combination of a specific tensorbay dataset file and its label.

    It contains the file remote path, label information of the file
    and the file metadata, such as timestamp.

    A RemoteData instance contains one or several types of labels.

    Arguments:
        remote_path: The file remote path.
        timestamp: The timestamp for the file.
        url: The URL instance used to get and update url.
        cache_path: The path to store the cache.

    Attributes:
        path: The file remote path.
        timestamp: The timestamp for the file.
        label: The :class:`~tensorbay.label.label.Label` instance that contains
                all the label information of the file.
        url: The :class:`~tensorbay.utility.file.URL` instance used to get and update url.

    """

    _T = TypeVar("_T", bound="RemoteData")

    def __init__(
        self,
        remote_path: str,
        *,
        timestamp: Optional[float] = None,
        url: Optional[URL] = None,
        cache_path: str = "",
    ) -> None:
        DataBase.__init__(self, timestamp)
        RemoteFileMixin.__init__(
            self,
            remote_path,
            url=url,
            cache_path=cache_path,
        )

    @classmethod
    def from_response_body(
        cls: Type[_T],
        body: Dict[str, Any],
        *,
        url: Optional[URL] = None,
        cache_path: str = "",
    ) -> _T:  # noqa: DAR101
        """Loads a :class:`RemoteData` object from a response body.

        Arguments:
            body: The response body which contains the information of a remote data,
                whose format should be like::

                    {
                        "remotePath": <str>,
                        "timestamp": <float>,
                        "url": <str>,
                        "label": {
                            "CLASSIFICATION": {...},
                            "BOX2D": {...},
                            "BOX3D": {...},
                            "POLYGON": {...},
                            "POLYLINE2D": {...},
                            "KEYPOINTS2D": {...},
                            "SENTENCE": {...}
                        }
                    }
            url: The URL instance used to get and update url.
            cache_path: The path to store the cache.

        Returns:
            The loaded :class:`RemoteData` object.

        """
        data = cls(
            body["remotePath"],
            timestamp=body.get("timestamp"),
            url=url,
            cache_path=cache_path,
        )
        data.label._loads(body["label"])  # pylint: disable=protected-access
        return data


class AuthData(DataBase, RemoteFileMixin):
    """AuthData is a combination of a specific cloud storaged file and its label.

    It contains the cloud storage file path, label information of the file
    and the file metadata, such as timestamp.

    An AuthData instance contains one or several types of labels.

    Arguments:
        cloud_path: The cloud file path.
        target_remote_path: The file remote path after uploading to tensorbay.
        timestamp: The timestamp for the file.
        url: The URL instance used to get and update url.

    Attributes:
        path: The cloud file path.
        timestamp: The timestamp for the file.
        label: The :class:`~tensorbay.label.label.Label` instance that contains
                all the label information of the file.
        url: The :class:`~tensorbay.utility.file.URL` instance used to get and update url.

    """

    def __init__(
        self,
        cloud_path: str,
        *,
        target_remote_path: Optional[str] = None,
        timestamp: Optional[float] = None,
        url: Optional[URL] = None,
    ) -> None:
        DataBase.__init__(self, timestamp)
        RemoteFileMixin.__init__(self, cloud_path, url=url)
        self._target_remote_path = target_remote_path

    @property
    def target_remote_path(self) -> str:
        """Return the target remote path of the auth data.

        Target remote path will be used when this data is uploaded to tensorbay, and the target
        remote path will be the uploaded file's remote path.

        Returns:
            The target remote path of the auth data.

        """
        if not self._target_remote_path:
            self._target_remote_path = self.path.split("/")[-1]

        return self._target_remote_path

    @target_remote_path.setter
    def target_remote_path(self, target_remote_path: str) -> None:
        self._target_remote_path = target_remote_path

    def get_callback_body(self) -> Dict[str, Any]:
        """Get the callback request body for uploading.

        Returns:
            The callback request body, which looks like::

                    {
                        "cloudPath": <str>,
                        "remotePath": <str>,
                        "label": {
                            "CLASSIFICATION": {...},
                            "BOX2D": {...},
                            "BOX3D": {...},
                            "POLYGON": {...},
                            "POLYLINE2D": {...},
                            "KEYPOINTS2D": {...},
                            "SENTENCE": {...}
                        }
                    }

        """
        body: Dict[str, Any] = {"cloudPath": self.path, "remotePath": self.target_remote_path}
        if self.label:
            body["label"] = self.label.dumps()
        return body
