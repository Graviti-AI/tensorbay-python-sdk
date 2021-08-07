#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Data.

:class:`Data` is the most basic data unit of a :class:`~tensorbay.dataset.dataset.Dataset`.
It contains path information of a data sample and its corresponding labels.

"""

import os
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

from ..label import Label
from ..utility import AttrsMixin, FileMixin, RemoteFileMixin, ReprMixin, attr, common_loads


class DataBase(AttrsMixin, ReprMixin):  # pylint: disable=too-few-public-methods
    """DataBase is a base class for the file and label combination.

    Arguments:
        timestamp: The timestamp for the file.

    Attributes:
        timestamp: The timestamp for the file.
        label: The :class:`~tensorbay.label.label.Label` instance that contains
            all the label information of the file.

    """

    _T = TypeVar("_T", bound="DataBase")
    _Type = Union["Data", "RemoteData", "AuthData"]

    _repr_attrs = ("timestamp", "label")

    timestamp: float = attr(is_dynamic=True)
    label: Label = attr()

    def __init__(self, timestamp: Optional[float] = None) -> None:
        if timestamp is not None:
            self.timestamp = timestamp

        self.label = Label()

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

    _T = TypeVar("_T", bound="Data")

    path: str = attr(key="localPath")

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


class RemoteData(DataBase, RemoteFileMixin):
    """RemoteData is a combination of a specific tensorbay dataset file and its label.

    It contains the file remote path, label information of the file
    and the file metadata, such as timestamp.

    A RemoteData instance contains one or several types of labels.

    Arguments:
        remote_path: The file remote path.
        timestamp: The timestamp for the file.
        _url_getter: The url getter of the remote file.

    Attributes:
        path: The file remote path.
        timestamp: The timestamp for the file.
        label: The :class:`~tensorbay.label.label.Label` instance that contains
                all the label information of the file.

    """

    _T = TypeVar("_T", bound="RemoteData")

    path: str = attr(key="remotePath")

    def __init__(
        self,
        remote_path: str,
        *,
        timestamp: Optional[float] = None,
        _url_getter: Optional[Callable[[str], str]] = None,
    ) -> None:
        DataBase.__init__(self, timestamp)
        RemoteFileMixin.__init__(self, remote_path, _url_getter=_url_getter)

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


class AuthData(DataBase, RemoteFileMixin):
    """AuthData is a combination of a specific cloud storaged file and its label.

    It contains the cloud storage file path, label information of the file
    and the file metadata, such as timestamp.

    An AuthData instance contains one or several types of labels.

    Arguments:
        cloud_path: The cloud file path.
        target_remote_path: The file remote path after uploading to tensorbay.
        timestamp: The timestamp for the file.
        _url_getter: The url getter of the remote file.

    Attributes:
        path: The cloud file path.
        timestamp: The timestamp for the file.
        label: The :class:`~tensorbay.label.label.Label` instance that contains
                all the label information of the file.

    """

    _T = TypeVar("_T", bound="AuthData")

    path: str = attr(key="cloudPath")

    def __init__(
        self,
        cloud_path: str,
        *,
        target_remote_path: Optional[str] = None,
        timestamp: Optional[float] = None,
        _url_getter: Optional[Callable[[str], str]] = None,
    ) -> None:
        DataBase.__init__(self, timestamp)
        RemoteFileMixin.__init__(self, cloud_path, _url_getter=_url_getter)
        self._target_remote_path = target_remote_path

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


_DATA_SUBCLASS = (("remotePath", RemoteData), ("localPath", Data), ("cloudPath", AuthData))
