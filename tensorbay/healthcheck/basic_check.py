#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Method check_basic.

:meth:`check_basic` checks whether :class:`~tensorbay.dataset.dataset.Dataset`
or :class:`~tensorbay.dataset.dataset.FusionDataset`
is empty and whether the :class:`~tensorbay.dataset.segment.Segment`
or :class:`~tensorbay.dataset.dataset.FusionDataset` in the object is empty.

"""

from typing import Iterator, Union

from ..dataset import Dataset, FusionDataset
from .report import Error


class BasicError(Error):
    """The base class of the basic error.

    Arguments:
         name: The dataset or segment name which has error.

    """

    def __init__(self, name: str) -> None:
        self._name = name


class EmptyDatasetError(BasicError):
    """The health check function for empty dataset.

    This error is raised to indicate that :class:`~tensorbay.dataset.dataset.Dataset`
    or :class:`~tensorbay.dataset.dataset.FusionDataset` is empty.

    """

    def __str__(self) -> str:
        return f"Dataset '{self._name}' is empty"


class EmptySegmentError(BasicError):
    """The health check function for empty segment.

    This error is raised to indicate that :class:`~tensorbay.dataset.segment.Segment`
    or :class:`~tensorbay.dataset.dataset.FusionDataset` is empty.

    """

    def __str__(self) -> str:
        return f"Segment '{self._name}' is empty"


def check_basic(dataset: Union[Dataset, FusionDataset]) -> Iterator[BasicError]:
    """The health check function for basic error.

    Arguments:
        dataset: The :class:`~tensorbay.dataset.dataset.Dataset` or
            :class:`~tensorbay.dataset.dataset.FusionDataset` needs to be checked.

    Yields:
        BasicError indicating that :class:`~tensorbay.dataset.dataset.Dataset`,
        :class:`~tensorbay.dataset.dataset.FusionDataset`,
        :class:`~tensorbay.dataset.segment.Segment` or
        :class:`~tensorbay.dataset.segment.FusionSegment` is empty.

    """
    if not dataset:
        yield EmptyDatasetError(dataset.name)
        return

    for segment in dataset:
        if not segment:
            yield EmptySegmentError(segment.name)
