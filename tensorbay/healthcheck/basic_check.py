#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#

"""Method check_basic.

:meth:`basic_check` checks whether :class:`Dataset` or :class:`FusionDataset`
is empty and whether the :class:`Segment` or :class:`FusionSegment` in the object is empty.

Todo:
    Add `../dataset/dataset.py` link.
    Add `../dataset/segment.py` link.

"""

from typing import Iterator, Union

from ..dataset import Dataset, FusionDataset
from .report import Error


class BasicError(Error):  # pylint: disable=too-few-public-methods
    """The base class of the basic error.

    Arguments:
         name: The dataset or segment name which has error.

    """

    def __init__(self, name: str) -> None:
        self._name = name


class EmptyDatasetError(BasicError):  # pylint: disable=too-few-public-methods
    """This error is raised to indicate that :class:`Dataset` or :class:`FusionDataset` is empty."""

    def __str__(self) -> str:
        return f"Dataset '{self._name}' is empty"


class EmptySegmentError(BasicError):  # pylint: disable=too-few-public-methods
    """This error is raised to indicate that :class:`Segment` or :class:`FusionSegment` is empty."""

    def __str__(self) -> str:
        return f"Segment '{self._name}' is empty"


def check_basic(dataset: Union[Dataset, FusionDataset]) -> Iterator[BasicError]:
    """The health check function for basic error.

    Arguments:
        dataset: The :class:`Dataset` or :class:`FusionDataset` needs to be checked.

    Yields:
        BasicError indicating that :class:`Dataset`, :class:`FusionDataset`,
        :class:`FusionSegment` or :class:`Segment` is empty.

    """
    if not dataset:
        yield EmptyDatasetError(dataset.name)
        return

    for segment in dataset:
        if not segment:
            yield EmptySegmentError(segment.name)
