#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Utility tools about iteration."""

from itertools import islice
from typing import Iterable, Iterator, Tuple, TypeVar

_T = TypeVar("_T")


def chunked(iterable: Iterable[_T], n: int) -> Iterator[Tuple[_T, ...]]:
    """Break an iterable instance into tuples of length n.

    Arguments:
        iterable: The input iterable instance which needs to be breaked into tuples of length n.
        n: The length of each yielded tuples.

    Yields:
        The tuples of length n.

    Examples:
        >>> list(chunked(range(9), 3))
        [(0, 1, 2), (3, 4, 5), (6, 7, 8)]

        The last yielded tuple may have fewer than n items if the length of the input iterable
        instance is not divisible by n:

        >>> list(chunked(range(10), 3))
        [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]

    """
    iterator = iter(iterable)

    while True:
        chunk = tuple(islice(iterator, n))
        if not chunk:
            return

        yield chunk
