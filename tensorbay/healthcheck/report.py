#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""HealthReport.

:class:`HealthReport` contains all the errors found through healthcheck
within :class:`~tensorbay.dataset.dataset.Dataset` or
:class:`~tensorbay.dataset.dataset.FusionDataset`, including the result of
basic checking and catalog checking.

"""


from collections import OrderedDict
from typing import Any, Callable, List, TypeVar

from ..utility import UserMutableMapping, UserSequence


class Error:
    """Base class of healthcheck errors."""

    def __str__(self) -> str:
        ...


class _ErrorContext:
    _S = TypeVar("_S", bound="_ErrorContext")

    def __init__(self, title: str) -> None:
        self._title = title

    def __enter__(self: _S) -> _S:
        print("-------------------------------------------")
        print(self._title)
        return self

    def __exit__(self, *_: Any) -> None:
        if not self:
            print("PASS")


class _ErrorSection(UserSequence[Error]):
    def __init__(self) -> None:
        self._data: List[Error] = []

    def append(self, error: Error) -> None:
        """Append a error to the end of the error list.

        Arguments:
            error: The error object needs to be appended.

        """
        self._data.append(error)
        print(f"    {error}")


class _ErrorList(_ErrorSection, _ErrorContext):
    def __init__(self, title: str) -> None:
        _ErrorSection.__init__(self)
        _ErrorContext.__init__(self, title)

    def append(self, error: Error) -> None:
        """Append a error to the end of the error list.

        Arguments:
            error: The error object needs to be appended.

        """
        if not self:
            print("FAILED")

        self._data.append(error)
        print(f"  {error}")


_T = TypeVar("_T")


class _ErrorDict(UserMutableMapping[_T, _ErrorSection], _ErrorContext):
    def __init__(self, title: str, key_printer: Callable[[_T], str] = str) -> None:
        _ErrorContext.__init__(self, title)
        self._data = OrderedDict()
        self._key_printer = key_printer

    def __getitem__(self, key: _T) -> _ErrorSection:
        try:
            return self._data.__getitem__(key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key: _T) -> _ErrorSection:
        if not self:
            print("FAILED")
        print(f"  {self._key_printer(key)}:")
        value = _ErrorSection()
        self._data.__setitem__(key, value)
        return value


class HealthReport:
    """:class:`HealthReport` is the result of the healthcheck, which contains all the errors."""

    def __init__(self) -> None:
        self.basic_reports = _ErrorList("Basic checking:")
        self.subcatalog_reports: _ErrorDict[str] = _ErrorDict(
            "Subcatalog checking:", lambda key: key
        )
