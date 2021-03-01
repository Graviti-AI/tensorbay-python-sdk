#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Data, Labels.

:class:`Data` is the most basic data unit of a :class:`~tensorbay.dataset.dataset.Dataset`.
It contains path information of a data sample and its corresponding labels.

A :class:`Data` instance contains one or several types of labels,
all of which are stored in :attr:`Data.labels`.

"""

import os
from http.client import HTTPResponse
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
from urllib.request import urlopen

from _io import BufferedReader

from ..label import (
    Classification,
    LabeledBox2D,
    LabeledBox3D,
    LabeledKeypoints2D,
    LabeledPolygon2D,
    LabeledPolyline2D,
    LabeledSentence,
    LabelType,
)
from ..utility import ReprMixin, ReprType, common_loads


class Labels(ReprMixin):
    """This class defines :attr:`Data.labels`.

    It contains growing types of labels referring to different tasks.

    """

    classification: Classification
    box2d: List[LabeledBox2D]
    box3d: List[LabeledBox3D]
    polygon2d: List[LabeledPolygon2D]
    polyline2d: List[LabeledPolyline2D]
    keypoints2d: List[LabeledKeypoints2D]
    sentence: List[LabeledSentence]

    _T = TypeVar("_T", bound="Labels")
    _repr_maxlevel = 2
    _repr_type = ReprType.INSTANCE
    _repr_attrs = tuple(label_type.value for label_type in LabelType)

    def __bool__(self) -> bool:
        for label_type in LabelType:
            if hasattr(self, label_type.value):
                return True
        return False

    def dumps(self) -> Dict[str, Any]:
        """Dumps all labels into a dict.

        Returns:
            Dumped labels dict, which looks like::

                {
                    "CLASSIFICATION": {...},
                    "BOX2D": {...},
                    "BOX3D": {...},
                    "POLYGON2D": {...},
                    "POLYLINE2D": {...},
                    "KEYPOINTS2D": {...},
                    "SENTENCE": {...},
                }

        """
        contents: Dict[str, Any] = {}
        for label_type in LabelType:
            labels = getattr(self, label_type.value, None)
            if labels is None:
                continue
            if label_type == LabelType.CLASSIFICATION:
                contents[label_type.name] = labels.dumps()
            else:
                contents[label_type.name] = [label.dumps() for label in labels]

        return contents

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads data from a dict containing the labels information.

        Arguments:
            contents: A dict containing the labels information, which looks like::

                    {
                        "CLASSIFICATION": {...},
                        "BOX2D": {...},
                        "BOX3D": {...},
                        "POLYGON2D": {...},
                        "POLYLINE2D": {...},
                        "KEYPOINTS2D": {...},
                        "SENTENCE": {...},
                    }

        Returns:
            A :class:`~tensorbay.label.label.Label` instance containing labels information
            from the given dict.

        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:
        for key, labels in contents.items():
            if key not in LabelType.__members__:
                continue

            label_type = LabelType[key]
            if label_type == LabelType.CLASSIFICATION:
                setattr(self, label_type.value, label_type.type.loads(labels))
            else:
                setattr(
                    self,
                    label_type.value,
                    [label_type.type.loads(label) for label in labels],
                )


class DataBase(ReprMixin):  # pylint: disable=too-few-public-methods
    """DataBase is a base class for the file and label combination.

    Arguments:
        path: The file path.
        timestamp: The timestamp for the file.

    Attributes:
        path: The file path.
        timestamp: The timestamp for the file.
        labels: The :class:`Labels` that contains all the label information of the file.

    """

    _Type = Union["Data", "RemoteData"]

    _repr_maxlevel = 3
    _repr_type = ReprType.INSTANCE
    _repr_attrs = ("timestamp", "labels")

    _T = TypeVar("_T", bound="DataBase")
    _PATH_KEY = ""

    def __init__(self, path: str, *, timestamp: Optional[float] = None) -> None:
        self.path = path
        if timestamp is not None:
            self.timestamp = timestamp

        self.labels = Labels()

    def _repr_head(self) -> str:
        return f'{self.__class__.__name__}("{self.path}")'

    @staticmethod
    def loads(contents: Dict[str, Any]) -> "_Type":
        """Loads :class:`Data` or :class:`RemoteData` from a dict containing data information.

        Arguments:
            contents: A dict containing the information of the data, which looks like::

                    {
                        "localPath" or "remotePath": <str>,
                        "timestamp": <float>,
                        "CLASSIFICATION": {...},
                        "BOX2D": {...},
                        "BOX3D": {...},
                        "POLYGON2D": {...},
                        "POLYLINE2D": {...},
                        "KEYPOINTS2D": {...},
                        "SENTENCE": {...},
                    }

        Returns:
            A :class:`Data` or :class:`RemoteData` instance containing the given dict information.

        """
        cls = Data if Data._PATH_KEY in contents else RemoteData  # pylint: disable=protected-access
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:
        self.path = contents[self._PATH_KEY]
        if "timestamp" in contents:
            self.timestamp = contents["timestamp"]

        self.labels = Labels.loads(contents)

    def _dumps(self) -> Dict[str, Any]:
        contents: Dict[str, Any] = {self._PATH_KEY: self.path}
        if hasattr(self, "timestamp"):
            contents["timestamp"] = self.timestamp

        contents.update(self.labels.dumps())
        return contents


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
        target_remote_path: The file remote path after uploading to tensorbay.
        timestamp: The timestamp for the file.
        labels: The :class:`Labels` that contains all the label information of the file.

    """

    _T = TypeVar("_T", bound="Data")
    _PATH_KEY = "localPath"

    def __init__(
        self,
        local_path: str,
        *,
        target_remote_path: Optional[str] = None,
        timestamp: Optional[float] = None,
    ) -> None:
        super().__init__(local_path, timestamp=timestamp)
        self._target_remote_path = target_remote_path

    def open(self) -> BufferedReader:
        """Return the binary file pointer of this file.

        The local file pointer will be obtained by build-in ``open()``.

        Returns:
            The local file pointer for this data.

        """
        return open(self.path, "rb")

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

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads :class:`Data` from a dict containing local data information.

        Arguments:
            contents: A dict containing the information of the data, which looks like::

                    {
                        "localPath": <str>,
                        "timestamp": <float>,
                        "CLASSIFICATION": {...},
                        "BOX2D": {...},
                        "BOX3D": {...},
                        "POLYGON2D": {...},
                        "POLYLINE2D": {...},
                        "KEYPOINTS2D": {...},
                        "SENTENCE": {...},
                    }

        Returns:
            A :class:`Data` instance containing information from the given dict.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the local data into a dict.

        Returns:
            Dumped data dict, which looks like::

                    {
                        "localPath": <str>,
                        "timestamp": <float>,
                        "CLASSIFICATION": {...},
                        "BOX2D": {...},
                        "BOX3D": {...},
                        "POLYGON2D": {...},
                        "POLYLINE2D": {...},
                        "KEYPOINTS2D": {...},
                        "SENTENCE": {...},
                    }

        """
        return super()._dumps()


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
        labels: The :class:`Labels` that contains all the label information of the file.

    """

    _T = TypeVar("_T", bound="RemoteData")
    _PATH_KEY = "remotePath"

    def __init__(
        self,
        remote_path: str,
        *,
        timestamp: Optional[float] = None,
        url_getter: Optional[Callable[[str], str]] = None,
    ) -> None:
        super().__init__(remote_path, timestamp=timestamp)
        self._url_getter = url_getter

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
        return urlopen(self.get_url())  # type: ignore[no-any-return]

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads :class:`RemoteData` from a dict containing remote data information.

        Arguments:
            contents: A dict containing the information of the data, which looks like::

                    {
                        "remotePath": <str>,
                        "timestamp": <float>,
                        "CLASSIFICATION": {...},
                        "BOX2D": {...},
                        "BOX3D": {...},
                        "POLYGON2D": {...},
                        "POLYLINE2D": {...},
                        "KEYPOINTS2D": {...},
                        "SENTENCE": {...},
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
                        "CLASSIFICATION": {...},
                        "BOX2D": {...},
                        "BOX3D": {...},
                        "POLYGON2D": {...},
                        "POLYLINE2D": {...},
                        "KEYPOINTS2D": {...},
                        "SENTENCE": {...},
                    }

        """
        return super()._dumps()
