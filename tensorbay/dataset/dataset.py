#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Notes, DatasetBase, Dataset and FusionDataset.

:class:`Notes` contains the basic information of a :class:`DatasetBase`.

:class:`DatasetBase` defines the basic concept of a dataset,
which is the top-level structure to handle your data files, labels and other additional information.

It represents a whole dataset contains several segments
and is the base class of :class:`Dataset` and :class:`FusionDataset`.

:class:`Dataset` is made up of data collected from only one sensor
or data without sensor information.
It consists of a list of :class:`~tensorbay.dataset.segment.Segment`.

:class:`FusionDataset` is made up of data collected from multiple sensors.
It consists of a list of :class:`~tensorbay.dataset.segment.FusionSegment`.

"""

import json
from typing import Any, Dict, KeysView, Sequence, Type, TypeVar, Union, overload

from ..label import Catalog
from ..utility import EqMixin, NameMixin, NameSortedList, ReprMixin, ReprType, common_loads
from .segment import FusionSegment, Segment

_T = TypeVar("_T", FusionSegment, Segment)


class Notes(ReprMixin, EqMixin):
    """This is a class stores the basic information of :class:`DatasetBase`.

    Arguments:
        is_continuous: Whether the data inside the dataset is time-continuous.

    """

    _T = TypeVar("_T", bound="Notes")

    _repr_attrs = ("is_continuous",)

    def __init__(self, is_continuous: bool = False) -> None:
        self.is_continuous = is_continuous

    def __getitem__(self, key: str) -> Any:
        try:
            return getattr(self, key)
        except AttributeError as error:
            raise KeyError(key) from error

    def _loads(self, contents: Dict[str, Any]) -> None:
        self.is_continuous = contents["isContinuous"]

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a :class:`Notes` instance from the given contents.

        Arguments:
            contents: The given dict containing the dataset notes::

                    {
                        "isContinuous": <boolean>
                    }

        Returns:
            The loaded :class:`Notes` instance.

        """
        return common_loads(cls, contents)

    def keys(self) -> KeysView[str]:
        """Return the valid keys within the notes.

        Returns:
            The valid keys within the notes.

        """
        keys = set()
        for attr in self._repr_attrs:
            if hasattr(self, attr):
                keys.add(attr)
        return KeysView(keys)  # type: ignore[arg-type]

    def dumps(self) -> Dict[str, Any]:
        """Dumps the notes into a dict.

        Returns:
            A dict containing all the information of the Notes::

                {
                    "isContinuous": <boolean>
                }

        """
        return {"isContinuous": self.is_continuous}


class DatasetBase(NameMixin, Sequence[_T]):  # pylint: disable=too-many-ancestors
    """This class defines the concept of a basic dataset.

    DatasetBase represents a whole dataset contains several segments
    and is the base class of :class:`Dataset` and :class:`FusionDataset`.

    A dataset with labels should contain a :class:`~tensorbay.label.catalog.Catalog`
    indicating all the possible values of the labels.

    Arguments:
        name: The name of the dataset.

    """

    _repr_type = ReprType.SEQUENCE

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._segments: NameSortedList[_T] = NameSortedList()
        self._catalog: Catalog = Catalog()
        self._notes = Notes()

    def __len__(self) -> int:
        return self._segments.__len__()

    @overload
    def __getitem__(self, index: int) -> _T:
        ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[_T]:
        ...

    def __getitem__(self, index: Union[int, slice]) -> Union[Sequence[_T], _T]:
        return self._segments.__getitem__(index)

    @property
    def catalog(self) -> Catalog:
        """Return the catalog of the dataset.

        Returns:
            The :class:`~tensorbay.label.catalog.Catalog` of the dataset.

        """
        return self._catalog

    @property
    def notes(self) -> Notes:
        """Return the notes of the dataset.

        Returns:
            The class:`Notes` of the dataset.

        """
        return self._notes

    def load_catalog(self, filepath: str) -> None:
        """Load catalog from a json file.

        Arguments:
            filepath: The path of the json file which contains the catalog information.

        """
        with open(filepath, "r") as fp:
            contents = json.load(fp)
        self._catalog = Catalog.loads(contents)

    def get_segment_by_name(self, name: str) -> _T:
        """Return the segment corresponding to the given name.

        Arguments:
            name: The name of the request segment.

        Returns:
            The segment which matches the input name.

        """
        return self._segments.get_from_name(name)

    def add_segment(self, segment: _T) -> None:
        """Add a segment to the dataset.

        Arguments:
            segment: The segment to be added.

        """
        self._segments.add(segment)


class Dataset(DatasetBase[Segment]):
    """This class defines the concept of dataset.

    Dataset is made up of data collected from only one sensor or data without sensor information.
    It consists of a list of :class:`~tensorbay.dataset.segment.Segment`.

    """

    def create_segment(self, segment_name: str = "") -> Segment:
        """Create a segment with the given name.

        Arguments:
            segment_name: The name of the segment to create, which default value is an empty string.

        Returns:
            The created :class:`~tensorbay.dataset.segment.Segment`.

        """
        segment = Segment(segment_name)
        self._segments.add(segment)
        return segment


class FusionDataset(DatasetBase[FusionSegment]):
    """This class defines the concept of fusion dataset.

    FusionDataset is made up of data collected from multiple sensors.
    It consists of a list of :class:`~tensorbay.dataset.segment.FusionSegment`.
    """

    def create_segment(self, segment_name: str = "") -> FusionSegment:
        """Create a fusion segment with the given name.

        Arguments:
            segment_name: The name of the fusion segment to create,
                which default value is an empty string.

        Returns:
            The created :class:`~tensorbay.dataset.segment.FusionSegment`.

        """
        segment = FusionSegment(segment_name)
        self._segments.add(segment)
        return segment
