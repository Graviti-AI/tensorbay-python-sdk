#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Pipeline and PipelineForIterable.

:class:`Pipeline` runs registered checker functions while healthchecking.
:class:`PipelineForIterable` is a healthcheck pipeline to processes iterable objects.

Checker functions can be registered to the healthcheck pipeline by :meth:`Pipeline.register` or
:meth:`PipelineForIterable.register <Pipeline.register>`.

"""

from typing import Callable, Generic, Iterable, Iterator, List, TypeVar

_A = TypeVar("_A")
_R = TypeVar("_R")
_Checker = Callable[[_A], Iterator[_R]]


class Pipeline(Generic[_A, _R]):
    """:class:`Pipeline` is a healthcheck pipeline to run registered checker functions."""

    _S = TypeVar("_S", bound="Pipeline[_A, _R]")

    def __init__(self) -> None:
        self._pipeline: List[_Checker[_A, _R]] = []

    def __call__(self, args: _A) -> Iterator[_R]:
        """Call the :class:`Pipeline` as a function.

        Arguments:
            args: The information needs to be checked.

        Yields:
            The checker function.

        """
        for checker in self._pipeline:
            yield from checker(args)

    def register(self, checker: _Checker[_A, _R]) -> _Checker[_A, _R]:
        """Decorator function to register checkers into pipeline.

        Arguments:
            checker: The checker function needs to be registered.

        Returns:
            The checker function unchanged.

        """
        self._pipeline.append(checker)
        return checker

    def copy(self: _S) -> _S:
        """Copy method to get a shallow copy of pipeline.

        Returns:
            A shallow copy of the pipeline.

        """
        pipeline = self.__class__()
        pipeline._pipeline = self._pipeline.copy()  # pylint: disable=protected-access
        return pipeline


class PipelineForIterable(Pipeline[_A, _R]):
    """Healthcheck pipeline for processing iterable objects."""

    def __call__(self, args: Iterable[_A]) -> Iterator[_R]:  # type: ignore[override]
        """Call the :class:`Pipeline` as a function.

        Arguments:
            args: The information needs to be checked.

        Yields:
            The checker function.

        """
        for arg in args:
            yield from super().__call__(arg)
