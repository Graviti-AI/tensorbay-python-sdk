#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Class about the diff.

:class:`DiffBase` defines the basic structure of a diff.

:class:`NotesDiff` defines the basic structure of a brief diff of notes.

:class:`CatalogDiff` defines the basic structure of a brief diff of catalog.

:class:`FileDiff` defines the basic structure of a brief diff of data file.

:class:`LabelDiff` defines the basic structure of a brief diff of data label.

:class:`SensorDiff` defines the basic structure of a brief diff of sensor.

:class:`DataDiff` defines the basic structure of a brief diff of data.

:class:`SegmentDiff` defines the basic structure of a brief diff of a segment.

:class:`DatasetDiff` defines the basic structure of a brief diff of a dataset.

"""

from typing import Any, Dict, List, Sequence, Tuple, Type, TypeVar, Union, overload

from ..utility import (
    AttrsMixin,
    NameMixin,
    ReprMixin,
    SortedNameList,
    UserSequence,
    attr,
    camel,
    common_loads,
)


class DiffBase(AttrsMixin, ReprMixin):
    """This class defines the basic structure of a diff.

    Attributes:
        action: The concrete action.

    """

    _T = TypeVar("_T", bound="DiffBase")

    _repr_attrs: Tuple[str, ...] = ("action",)

    action: str = attr()

    def __init__(self, action: str) -> None:
        self.action = action

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a :class:`DiffBase` instance from the given contents.

        Arguments:
            contents: A dict containing all the information of the diff::

                    {
                        "action": <str>
                    }

        Returns:
            A :class:`DiffBase` instance containing all the information in the given contents.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps all the information of the diff into a dict.

        Returns:
            A dict containing all the information of the diff::

                {
                    "action": <str>
                }

        """
        return self._dumps()


class NotesDiff(DiffBase):
    """This class defines the basic structure of a brief diff of notes."""


class CatalogDiff(DiffBase):
    """This class defines the basic structure of a brief diff of catalog."""


class FileDiff(DiffBase):
    """This class defines the basic structure of a brief diff of data file."""


class LabelDiff(DiffBase):
    """This class defines the basic structure of a brief diff of data label."""


class SensorDiff(DiffBase):
    """This class defines the basic structure of a brief diff of sensor."""


class DataDiff(DiffBase):
    """This class defines the basic structure of a diff statistic.

    Attributes:
        remote_path: The remote path.
        action: The action of data.
        file: The brief diff information of the file.
        label: The brief diff information of the labels.

    """

    _T = TypeVar("_T", bound="DataDiff")

    _repr_attrs = ("remote_path", "action")

    remote_path: str = attr(key=camel)
    file: FileDiff = attr()
    label: LabelDiff = attr()

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a :class:`DataDiff` instance from the given contents.

        Arguments:
            contents: A dict containing all the brief diff information of data::

                     {
                        "remotePath": <str>,
                        "action": <str>,
                        "file": {
                            "action": <str>
                        }
                        "label": {
                            "action": <str>
                        }
                    }

        Returns:
            A :class:`DataDiff` instance containing all the information in the given contents.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps all the brief diff information of data into a dict.

        Returns:
            A dict containing all the brief diff information of data::

                 {
                    "remotePath": <str>,
                    "action": <str>,
                    "file": {
                        "action": <str>
                    }
                    "label": {
                        "action": <str>
                    }
                }

        """
        return self._dumps()


class SegmentDiff(UserSequence[DataDiff], NameMixin):
    """This class defines the basic structure of a brief diff of a segment.

    Arguments:
        name: The segment name.
        action: The action of a segment.

    """

    _repr_attrs = ("name", "action")

    def __init__(self, name: str, action: str) -> None:
        super().__init__(name)

        self.action = action
        self._data: List[DataDiff] = []


class DatasetDiff(Sequence[SegmentDiff], NameMixin):  # pylint: disable=too-many-ancestors
    """This class defines the basic structure of a brief diff of a dataset.

    Arguments:
        name: The segment name.
        action: The action of a segment.

    """

    _repr_attrs = ("name", "action")

    def __init__(self, name: str) -> None:
        super().__init__(name)

        self._segments: SortedNameList[SegmentDiff] = SortedNameList()

    def __len__(self) -> int:
        return self._segments.__len__()

    @overload
    def __getitem__(self, index: Union[int, str]) -> SegmentDiff:
        ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[SegmentDiff]:
        ...

    def __getitem__(
        self, index: Union[int, str, slice]
    ) -> Union[Sequence[SegmentDiff], SegmentDiff]:
        return self._segments.__getitem__(index)

    def __contains__(self, key: Any) -> bool:
        return self._segments.__contains__(key)
