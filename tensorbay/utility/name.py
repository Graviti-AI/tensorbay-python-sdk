#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""NameMixin, SortedNameList and NameList.

:class:`NameMixin` is a mixin class for instance which has immutable name and mutable description.

:class:`SortedNameList` is a sorted sequence class which contains :class:`NameMixin`.
It is maintained in sorted order according to the 'name' of :class:`NameMixin`.

:class:`NameList` is a list of named elements, supports searching the element by its name.

"""

from bisect import bisect_left, bisect_right
from typing import Any, Dict, Iterable, List, Tuple, TypeVar, Union, overload

from .attr import AttrsMixin, attr
from .repr import ReprMixin
from .user import UserSequence


class NameMixin(AttrsMixin, ReprMixin):
    """A mixin class for instance which has immutable name and mutable description.

    Arguments:
        name: Name of the class.
        description: Description of the class.

    Attributes:
        name: Name of the class.

    """

    _P = TypeVar("_P", bound="NameMixin")

    _name: str = attr(key="name")
    description: str = attr(default="")

    def __init__(self, name: str, description: str = "") -> None:
        self._name = name
        self.description = description

    def _repr_head(self) -> str:
        return f'{self.__class__.__name__}("{self._name}")'

    @property
    def name(self) -> str:
        """Return name of the instance.

        Returns:
            Name of the instance.

        """
        return self._name


_T = TypeVar("_T", bound=NameMixin)


class NameList(UserSequence[_T]):
    """NameList is a list of named elements, supports searching the element by its name."""

    def __init__(self, values: Iterable[_T] = ()) -> None:
        self._data: List[_T] = []
        self._mapping: Dict[str, _T] = {}

        for value in values:
            self.append(value)

    @overload
    def __getitem__(self, index: Union[int, str]) -> _T:
        ...

    @overload
    def __getitem__(self, index: slice) -> List[_T]:
        ...

    def __getitem__(self, index: Union[int, str, slice]) -> Union[_T, List[_T]]:
        if isinstance(index, str):
            return self._mapping.__getitem__(index)

        return self._data.__getitem__(index)

    def __contains__(self, key: Any) -> bool:
        return self._mapping.__contains__(key)

    def keys(self) -> Tuple[str, ...]:
        """Get all element names.

        Returns:
            A tuple containing all elements names.

        """
        return tuple(item.name for item in self._data)

    def append(self, value: _T) -> None:
        """Append element to the end of the NameList.

        Arguments:
            value: Element to be appended to the NameList.

        Raises:
            KeyError: When the name of the appending object already exists in the NameList.

        """
        if value.name in self._mapping:
            raise KeyError(f'name "{value.name}" is duplicated')

        self._data.append(value)
        self._mapping[value.name] = value


class SortedNameList(UserSequence[_T]):
    """SortedNameList is a sorted sequence which contains element with name.

    It is maintained in sorted order according to the 'name' attr of the element.

    """

    def __init__(self) -> None:
        self._data: List[_T] = []
        self._names: List[str] = []

    @overload
    def __getitem__(self, index: Union[int, str]) -> _T:
        ...

    @overload
    def __getitem__(self, index: slice) -> List[_T]:
        ...

    def __getitem__(self, index: Union[int, str, slice]) -> Union[_T, List[_T]]:
        if isinstance(index, str):
            index = self._search(index)

        return self._data.__getitem__(index)

    def __delitem__(self, index: Union[int, str, slice]) -> None:
        if isinstance(index, str):
            index = self._search(index)

        self._data.__delitem__(index)
        self._names.__delitem__(index)

    def __contains__(self, key: Any) -> bool:
        try:
            self._search(key)
            return True
        except (KeyError, TypeError):
            return False

    def _search(self, key: str) -> int:
        index = bisect_left(self._names, key)
        if index == len(self._names) or self._names[index] != key:
            raise KeyError(key)

        return index

    def add(self, value: _T) -> None:
        """Store element in name sorted list.

        Arguments:
            value: The element needs to be added to the list.

        Raises:
            KeyError: If the name of the added value exists in the list.

        """
        name = value.name
        index = bisect_right(self._names, name)
        if index != 0 and self._names[index - 1] == name:
            raise KeyError(f'Name "{name}" already exists!')

        self._data.insert(index, value)
        self._names.insert(index, name)

    def keys(self) -> Tuple[str, ...]:
        """Get all element names.

        Returns:
            A tuple containing all elements names.

        """
        return tuple(self._names)
