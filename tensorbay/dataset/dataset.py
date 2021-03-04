#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""DatasetBase, Dataset and FusionDataset.

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
from typing import Sequence, TypeVar, Union, overload

from ..label import Catalog
from ..utility import NameMixin, NameSortedList, ReprType
from .segment import FusionSegment, Segment

_T = TypeVar("_T", FusionSegment, Segment)


class DatasetBase(NameMixin, Sequence[_T]):  # pylint: disable=too-many-ancestors
    """This class defines the concept of a basic dataset.

    DatasetBase represents a whole dataset contains several segments
    and is the base class of :class:`Dataset` and :class:`FusionDataset`.

    A dataset with labels should contain a :class:`~tensorbay.label.catalog.Catalog`
    indicating all the possible values of the labels.

    Arguments:
        name: The name of the dataset.
        is_continuous: Whether the data inside the dataset is time-continuous.

    """

    _repr_type = ReprType.SEQUENCE

    def __init__(self, name: str, is_continuous: bool = False) -> None:
        super().__init__(name)
        self._segments: NameSortedList[_T] = NameSortedList()
        self._catalog: Catalog = Catalog()
        self._is_continuous = is_continuous

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
    def is_continuous(self) -> bool:
        """Return whether the data in dataset is time-continuous or not.

        Returns:
            `True` if the data is time-continuous, otherwise `False`.

        """
        return self._is_continuous

    @property
    def catalog(self) -> Catalog:
        """Return the catalog of the dataset.

        Returns:
            The :class:`~tensorbay.label.catalog.Catalog` of the dataset.

        """
        return self._catalog

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
