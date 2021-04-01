#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Segment and FusionSegment.

Segment is a concept in :class:`~tensorbay.dataset.dataset.Dataset`.
It is the structure that composes :class:`~tensorbay.dataset.dataset.Dataset`,
and consists of a series of :class:`~tensorbay.dataset.data.Data` without sensor information.

Fusion segment is a concept in :class:`~tensorbay.dataset.dataset.FusionDataset`.
It is the structure that composes :class:`~tensorbay.dataset.dataset.FusionDataset`,
and consists of a list of :class:`~tensorbay.dataset.frame.Frame`
along with multiple :class:`~tensorbay.sensor.sensor.Sensors`.

"""

from typing import TYPE_CHECKING, Any, Callable, List, Optional, TypeVar

from ..sensor import Sensors
from ..utility import NameMixin, ReprType, UserMutableSequence
from .data import DataBase
from .frame import Frame

if TYPE_CHECKING:
    from ..client.dataset import DatasetClient, FusionDatasetClient


class Segment(NameMixin, UserMutableSequence["DataBase._Type"]):
    """This class defines the concept of segment.

    Segment is a concept in :class:`~tensorbay.dataset.dataset.Dataset`.
    It is the structure that composes :class:`~tensorbay.dataset.dataset.Dataset`,
    and consists of a series of :class:`~tensorbay.dataset.data.Data` without sensor information.

    If the segment is inside of a time-continuous :class:`~tensorbay.dataset.dataset.Dataset`,
    the time continuity of the data should be indicated by
    :meth`~graviti.dataset.data.Data.remote_path`.

    Since :class:`Segment` extends :class:`~tensorbay.utility.user.UserMutableSequence`,
    its basic operations are the same as a list's.

    To initialize a Segment and add a :class:`~tensorbay.dataset.data.Data` to it:

    .. code:: python

        segment = Segment(segment_name)
        segment.append(Data())

    Arguments:
        name: The name of the segment, whose default value is an empty string.
        client: The DatasetClient if you want to read the segment from tensorbay.

    """

    _T = TypeVar("_T", bound="Segment")

    _repr_type = ReprType.SEQUENCE

    def __init__(self, name: str = "", client: Optional["DatasetClient"] = None) -> None:
        super().__init__(name)

        self._data: List[DataBase._Type]
        if client:
            self._client = client.get_segment(name)
            self._data = list(self._client.list_data())
        else:
            self._data = []

    def sort(
        self,
        *,
        key: Callable[["DataBase._Type"], Any] = lambda data: data.path,
        reverse: bool = False,
    ) -> None:
        """Sort the list in ascending order and return None.

        The sort is in-place (i.e. the list itself is modified) and stable (i.e. the
        order of two equal elements is maintained).

        Arguments:
            key: If a key function is given, apply it once to each item of the segment,
                and sort them according to their function values in ascending or descending order.
                By default, the data within the segment is sorted by fileuri.
            reverse: The reverse flag can be set as True to sort in descending order.

        """
        self._data.sort(key=key, reverse=reverse)


class FusionSegment(NameMixin, UserMutableSequence[Frame]):
    """This class defines the concept of fusion segment.

    Fusion segment is a concept in :class:`~tensorbay.dataset.dataset.FusionDataset`.
    It is the structure that composes :class:`~tensorbay.dataset.dataset.FusionDataset`,
    and consists of a list of :class:`~tensorbay.dataset.frame.Frame`.

    Besides, a fusion segment contains multiple :class:`~tensorbay.sensor.sensor.Sensors`
    correspoinding to the :class:`~tensorbay.dataset.data.Data`
    under each :class:`~tensorbay.dataset.frame.Frame`.

    If the segment is inside of a time-continuous :class:`~tensorbay.dataset.dataset.FusionDataset`,
    the time continuity of the frames should be indicated by the index inside the fusion segment.

    Since :class:`FusionSegment` extends :class:`~tensorbay.utility.user.UserMutableSequence`,
    its basic operations are the same as a list's.

    To initialize a :class:`FusionSegment` and add a
    :class:`~tensorbay.dataset.frame.Frame` to it:

    .. code:: python

        fusion_segment = FusionSegment(fusion_segment_name)
        frame = Frame()
        ...
        fusion_segment.append(frame)

    Arguments:
        name: The name of the fusion segment, whose default value is an empty string.
        client: The FusionDatasetClient if you want to read the segment from tensorbay.

    """

    _T = TypeVar("_T", bound="FusionSegment")

    _repr_type = ReprType.SEQUENCE
    _repr_attrs = ("sensors",)
    _repr_maxlevel = 2

    def __init__(self, name: str = "", client: Optional["FusionDatasetClient"] = None) -> None:
        super().__init__(name)
        self.sensors = Sensors()

        self._data: List[Frame]
        if client:
            self._client = client.get_segment(name)
            self._data = list(self._client.list_frames())
            self.sensors = self._client.get_sensors()
        else:
            self._data = []
