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
along with multiple :class:`~tensorbay.sensor.sensor.Sensor`.

"""

from typing import Any, Callable, Dict, List, Type, TypeVar

from ..sensor import Sensor
from ..utility import NameMixin, NameSortedDict, ReprType, UserMutableSequence, common_loads
from .data import DataBase
from .frame import Frame


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

    """

    _T = TypeVar("_T", bound="Segment")

    _repr_type = ReprType.SEQUENCE

    def __init__(self, name: str = "") -> None:
        super().__init__(name)
        self._data: List[DataBase._Type] = []

    def _loads(self, contents: Dict[str, Any]) -> None:
        super()._loads(contents)
        self._data = [DataBase.loads(data) for data in contents["data"]]

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a :class:`Segment` object from a dict containing the segment information.

        Arguments:
            contents: A dict containing the information of a Segment,
                whose format should be like::

                    {
                        "name": <str>
                        "description": <str>
                        "data": [
                            data_dict{...},
                            data_dict{...},
                            ...
                            ...
                        ]
                    }

        Returns:
            The loaded :class:`Segment` object.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the segment into a dict.

        Returns:
            A dict contains the name and the data of the segment.

        """
        contents: Dict[str, Any] = super()._dumps()
        contents["data"] = [data.dumps() for data in self._data]

        return contents

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

    Besides, a fusion segment contains multiple :class:`~tensorbay.sensor.sensor.Sensor`
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

    """

    _T = TypeVar("_T", bound="FusionSegment")

    _repr_type = ReprType.SEQUENCE
    _repr_attrs = ("sensors",)
    _repr_maxlevel = 2

    def __init__(self, name: str = "") -> None:
        super().__init__(name)
        self._data: List[Frame] = []
        self.sensors: NameSortedDict[Sensor] = NameSortedDict()

    def _loads(self, contents: Dict[str, Any]) -> None:
        super()._loads(contents)
        self._data = []
        self.sensors = NameSortedDict()
        for sensor in contents["sensors"]:
            self.sensors.add(Sensor.loads(sensor))
        for frame in contents["frames"]:
            self._data.append(Frame.loads(frame))

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Load a :class:`FusionSegment` object from a dict containing the information.

        Arguments:
            contents: A dict containing the information of a fusion segment,
                whose format should be like::

                    {
                        "name": <str>
                        "description": <str>
                        "sensors": [
                            sensor_dict{...},
                            sensor_dict{...},
                            ...
                            ...
                        ]
                        "frames": [
                            frame_dict{...},
                            frame_dict{...},
                            ...
                            ...
                        ]
                    }

        Returns:
            The loaded :class:`FusionSegment` object.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the fusion segment into a dict.

        Returns:
            A dictonary contains the name, the sensors and the frames of the fusion segment.

        """
        contents: Dict[str, Any] = super()._dumps()
        contents["sensors"] = [sensor.dumps() for sensor in self.sensors.values()]
        contents["frames"] = [frame.dumps() for frame in self._data]

        return contents
