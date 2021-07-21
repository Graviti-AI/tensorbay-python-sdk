#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Data.

:class:`Data` is the most basic data unit of a :class:`~tensorbay.dataset.dataset.Dataset`.
It contains path information of a data sample and its corresponding labels.

"""

import os
from http.client import HTTPResponse
from string import printable
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union
from urllib.parse import quote, urljoin
from urllib.request import pathname2url, urlopen

from _io import BufferedReader

from ..label import Label
from ..utility import AttrsMixin, ReprMixin, ReprType, attr, common_loads


class DataBase(AttrsMixin, ReprMixin):  # pylint: disable=too-few-public-methods
    """DataBase is a base class for the file and label combination.

    Arguments:
        path: The file path.
        timestamp: The timestamp for the file.

    Attributes:
        path: The file path.
        timestamp: The timestamp for the file.
        label: The :class:`~tensorbay.label.label.Label` instance that contains
            all the label information of the file.

    """

    _T = TypeVar("_T", bound="DataBase")
    _Type = Union["Data", "RemoteData", "AuthData"]

    _repr_type = ReprType.INSTANCE
    _repr_attrs = ("timestamp", "label")
    _repr_maxlevel = 3

    _PATH_KEY = ""

    timestamp: float = attr(is_dynamic=True)
    label: Label = attr()

    def __init__(self, path: str, *, timestamp: Optional[float] = None) -> None:
        self.path = path
        if timestamp is not None:
            self.timestamp = timestamp

        self.label = Label()

    def _repr_head(self) -> str:
        return f'{self.__class__.__name__}("{self.path}")'

    @staticmethod
    def loads(contents: Dict[str, Any]) -> "_Type":
        """Loads data subclass from a dict containing data information.

        Arguments:
            contents: A dict containing the information of the data, which looks like::

                    {
                        "localPath", "remotePath" or "cloudPath": <str>,
                        "timestamp": <float>,
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

        Returns:
            A :class:`Data`, :class:`RemoteData` or :class:`AuthData` instance containing
            information from the given dict.

        Raises:
            KeyError: When the "localPath", "remotePath" or "cloudPath" not in contents.

        """
        for key, value in _DATA_SUBCLASS:
            if key in contents:
                return common_loads(value, contents)
        raise KeyError("Must contain 'localPath', 'remotePath' or 'cloudPath' in contents.")


class Data(DataBase):
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

    _T = TypeVar("_T", bound="Data")

    _PATH_KEY = "localPath"
    path: str = attr(key=_PATH_KEY)

    def __init__(
        self,
        local_path: str,
        *,
        target_remote_path: Optional[str] = None,
        timestamp: Optional[float] = None,
    ) -> None:
        super().__init__(local_path, timestamp=timestamp)
        self._target_remote_path = target_remote_path

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads :class:`Data` from a dict containing local data information.

        Arguments:
            contents: A dict containing the information of the data, which looks like::

                    {
                        "localPath": <str>,
                        "timestamp": <float>,
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

        Returns:
            A :class:`Data` instance containing information from the given dict.

        """
        return common_loads(cls, contents)

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

    def open(self) -> BufferedReader:
        """Return the binary file pointer of this file.

        The local file pointer will be obtained by build-in ``open()``.

        Returns:
            The local file pointer for this data.

        """
        return open(self.path, "rb")

    def dumps(self) -> Dict[str, Any]:
        """Dumps the local data into a dict.

        Returns:
            Dumped data dict, which looks like::

                    {
                        "localPath": <str>,
                        "timestamp": <float>,
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
        return super()._dumps()

    def get_url(self) -> str:
        """Return the url of the local data file.

        Returns:
            The url of the local data.

        """
        return urljoin("file:", pathname2url(os.path.abspath(self.path)))


class RemoteData(DataBase):
    """RemoteData is a combination of a specific tensorbay dataset file and its label.

    It contains the file remote path, label information of the file
    and the file metadata, such as timestamp.

    A RemoteData instance contains one or several types of labels.

    Arguments:
        remote_path: The file remote path.
        timestamp: The timestamp for the file.
        url_getter: The url getter of the remote file.

    Attributes:
        path: The file remote path.
        timestamp: The timestamp for the file.
        label: The :class:`~tensorbay.label.label.Label` instance that contains
                all the label information of the file.

    """

    _T = TypeVar("_T", bound="RemoteData")

    _PATH_KEY = "remotePath"
    path: str = attr(key=_PATH_KEY)

    def __init__(
        self,
        remote_path: str,
        *,
        timestamp: Optional[float] = None,
        url_getter: Optional[Callable[[str], str]] = None,
    ) -> None:
        super().__init__(remote_path, timestamp=timestamp)
        self._url_getter = url_getter

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads :class:`RemoteData` from a dict containing remote data information.

        Arguments:
            contents: A dict containing the information of the data, which looks like::

                    {
                        "remotePath": <str>,
                        "timestamp": <float>,
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

        Returns:
            A :class:`Data` instance containing information from the given dict.

        """
        return common_loads(cls, contents)

    def get_url(self) -> str:
        """Return the url of the data hosted by tensorbay.

        Returns:
            The url of the data.

        Raises:
            ValueError: When the url_getter is missing.

        """
        if not self._url_getter:
            raise ValueError(
                f"The file URL cannot be got because {self._repr_head()} has no url_getter"
            )

        return self._url_getter(self.path)

    def open(self) -> HTTPResponse:
        """Return the binary file pointer of this file.

        The remote file pointer will be obtained by ``urllib.request.urlopen()``.

        Returns:
            The remote file pointer for this data.

        """
        return urlopen(quote(self.get_url(), safe=printable))  # type: ignore[no-any-return]

    def dumps(self) -> Dict[str, Any]:
        """Dumps the remote data into a dict.

        Returns:
            Dumped data dict, which looks like::

                    {
                        "remotePath": <str>,
                        "timestamp": <float>,
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
        return super()._dumps()


class AuthData(DataBase):
    """AuthData is a combination of a specific cloud storaged file and its label.

    It contains the cloud storage file path, label information of the file
    and the file metadata, such as timestamp.

    An AuthData instance contains one or several types of labels.

    Arguments:
        cloud_path: The cloud file path.
        target_remote_path: The file remote path after uploading to tensorbay.
        timestamp: The timestamp for the file.
        url_getter: The url getter of the remote file.

    Attributes:
        path: The cloud file path.
        timestamp: The timestamp for the file.
        label: The :class:`~tensorbay.label.label.Label` instance that contains
                all the label information of the file.

    """

    _T = TypeVar("_T", bound="AuthData")

    _PATH_KEY = "cloudPath"
    path: str = attr(key=_PATH_KEY)

    def __init__(
        self,
        cloud_path: str,
        *,
        target_remote_path: Optional[str] = None,
        timestamp: Optional[float] = None,
        url_getter: Optional[Callable[[str], str]] = None,
    ) -> None:
        super().__init__(cloud_path, timestamp=timestamp)
        self._target_remote_path = target_remote_path
        self._url_getter = url_getter

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads :class:`AuthData` from a dict containing remote data information.

        Arguments:
            contents: A dict containing the information of the data, which looks like::

                    {
                        "cloudPath": <str>,
                        "timestamp": <float>,
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

        Returns:
            An :class:`AuthData` instance containing information from the given dict.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the auth data into a dict.

        Returns:
            Dumped data dict, which looks like::

                    {
                        "cloudPath": <str>,
                        "timestamp": <float>,
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
        return super()._dumps()

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

    def get_url(self) -> str:
        """Return the url of the auth data.

        Returns:
            The url of the auth data.

        Raises:
            ValueError: When the url_getter is missing.

        """
        if not self._url_getter:
            raise ValueError(
                f"The file URL cannot be got because {self._repr_head()} has no url_getter"
            )

        return self._url_getter(self.path)

    def open(self) -> HTTPResponse:
        """Return the binary file pointer of this file.

        Returns:
            The cloud file pointer of this file path.

        """
        return urlopen(quote(self.get_url(), safe=printable))  # type: ignore[no-any-return]


_DATA_SUBCLASS = (("remotePath", RemoteData), ("localPath", Data), ("cloudPath", AuthData))
