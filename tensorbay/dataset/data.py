#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Data, Labels.

:class:`Data` is the most basic data unit of a :class:`~graviti.dataset.dataset.Dataset`.
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
from ..utility import TBRN, ReprMixin, ReprType, common_loads


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
        """Dumps all labels into a dictionary.

        Returns:
            Dumped labels dictionary, which looks like::

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
        """Loads data from a dictionary containing the labels information.

        Arguments:
            contents: A dictionary containing the labels information, which looks like::

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
            A :class:`Label` instance containing labels information from the given dictionary.

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


class Data(ReprMixin):
    """Data is the most basic data unit of a :class:`~graviti.dataset.dataset.Dataset`.

    It contains the local and/or remote path of a data sample,
    sample's labels information, as well as some other information, such as timestamp.

    A Data instance contains one or several types of labels.

    Arguments:
        fileuri: The file uri of the data sample.
        remote_path: The remote_path of the data sample.
        timestamp: The timestamp for the data sample.
        url_getter: The url getter of Data.

    Attributes:
        timestamp: The timestamp for the data sample.
        labels: The :class:`Labels` that contains all the label information
          referring to the sample.

    """

    _T = TypeVar("_T", bound="Data")
    _repr_maxlevel = 3
    _repr_type = ReprType.INSTANCE
    _repr_attrs = ("fileuri", "timestamp", "labels")

    def __init__(
        self,
        fileuri: Union[str, TBRN],
        *,
        remote_path: Optional[str] = None,
        timestamp: Optional[float] = None,
        url_getter: Optional[Callable[[TBRN], str]] = None,
    ) -> None:
        self._set_fileuri(fileuri)

        if timestamp is not None:
            self.timestamp = timestamp

        self._remote_path = remote_path  # The remote storage location of the data
        self._url_getter = url_getter
        self.labels = Labels()

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads data from a dictionary containing data information.

        Arguments:
            contents: A dictionary containing the information of the data, which looks like::

                    {
                        "fileuri": <str>,
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
            A :class:`Data` instance containing information from the given dictionary.

        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:
        fileuri = contents["fileuri"]
        if "timestamp" in contents:
            self.timestamp = contents["timestamp"]

        self._set_fileuri(fileuri)

        self.labels = Labels.loads(contents)
        self._remote_path = None
        self._url_getter = None

    def _set_fileuri(self, fileuri: Union[str, TBRN]) -> None:
        if isinstance(fileuri, str) and fileuri.startswith("tb:"):
            fileuri = TBRN(tbrn=fileuri)
        self._fileuri = fileuri
        self._local_path = self._fileuri if isinstance(self._fileuri, str) else ""

    def dumps(self) -> Dict[str, Any]:
        """Dumps a data into a dictionary.

        Returns:
            Dumped data dictionary, which looks like::

                    {
                        "fileuri": <str>,
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
        contents: Dict[str, Any] = {"fileuri": str(self._fileuri)}
        if hasattr(self, "timestamp"):
            contents["timestamp"] = self.timestamp

        contents.update(self.labels.dumps())
        return contents

    def _repr_head(self) -> str:
        return f'{self.__class__.__name__}("{self._fileuri}")'

    def get_url(self) -> str:
        """Return the url of the data hosted by tensorbay.

        Returns:
            The url of the data.

        Raises:
            ValueError: When the url_getter is missing.

        """
        if not self._url_getter:
            raise ValueError(
                f"{self._repr_head()} has no url_getter, it is probably not a remote file"
            )

        return self._url_getter(self.tbrn)

    def open(self) -> Union[BufferedReader, HTTPResponse]:
        """Return the binary file pointer of this file.

        The file pointer will be obtained by build-in ``open()`` for local files,
        or by ``urllib.request.urlopen()`` for remote files.

        Returns:
            The file pointer for this data.

            The returned class will be ``_io.BufferedReader`` for local files,
            and ``http.client.HTTPResponse`` for remote files.

        """
        if self._local_path:
            return open(self._local_path, "rb")

        return urlopen(self.get_url())

    @property
    def fileuri(self) -> Union[str, TBRN]:
        """Return the fileuri of the data.

        Returns:
            The fileuri of the data.

        """
        return self._fileuri

    @property
    def tbrn(self) -> TBRN:
        """Return the :ref:`features:TBRN` of the data.

        Returns:
            The TBRN of the data.

        Raises:
            ValueError: When the TBRN is missing.

        """
        if not isinstance(self._fileuri, TBRN):
            raise ValueError(f"{self._repr_head()} has no TBRN, it is probably not a remote file")

        return self._fileuri

    @property
    def local_path(self) -> str:
        """Return the local path of the data.

        Returns:
            The local path of the data.

        """
        return self._local_path

    @property
    def remote_path(self) -> str:
        """Return the remote path of the data.

        Returns:
            The remote path of the data.

        """
        if self._remote_path:
            return self._remote_path

        if isinstance(self._fileuri, TBRN):
            return self._fileuri.remote_path

        return os.path.basename(self._fileuri)

    @remote_path.setter
    def remote_path(self, remote_path: str) -> None:
        """Set the remote path of the data.

        Arguments:
            remote_path: The remote path to set.

        """
        self._remote_path = remote_path
