#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""UserSequence, UserMutableSequence, UserMapping and UserMutableMapping.

:class:`UserSequence` is a user-defined wrapper around sequence objects.

:class:`UserMutableSequence` is a user-defined wrapper around mutable sequence objects.

:class:`UserMapping` is a user-defined wrapper around mapping objects.

:class:`UserMutableMapping` is a user-defined wrapper around mutable mapping objects.

"""

from sys import maxsize
from typing import (
    AbstractSet,
    Any,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    ValuesView,
    overload,
)

from .repr import ReprMixin, ReprType

_T = TypeVar("_T")
_K = TypeVar("_K")
_V = TypeVar("_V")


class UserSequence(Sequence[_T], ReprMixin):  # pylint: disable=too-many-ancestors
    """UserSequence is a user-defined wrapper around sequence objects."""

    _data: Sequence[_T]

    _repr_type = ReprType.SEQUENCE

    def __len__(self) -> int:
        return self._data.__len__()

    @overload
    def __getitem__(self, index: int) -> _T:
        ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[_T]:
        ...

    def __getitem__(self, index: Union[int, slice]) -> Union[Sequence[_T], _T]:
        return self._data.__getitem__(index)

    def __contains__(self, value: Any) -> bool:
        return self._data.__contains__(value)

    def __iter__(self) -> Iterator[_T]:
        return self._data.__iter__()

    def __reversed__(self) -> Iterator[_T]:
        return self._data.__reversed__()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self._data.__eq__(other._data)

    def index(self, value: _T, start: int = 0, stop: int = maxsize) -> int:
        """Return the first index of the value.

        Arguments:
            value: The value to be found.
            start: The start index of the subsequence.
            stop: The end index of the subsequence.

        Returns:
            The First index of value.

        """
        return self._data.index(value, start, stop)

    def count(self, value: _T) -> int:
        """Return the number of occurrences of value.

        Arguments:
            value: The value to be counted the number of occurrences.

        Returns:
            The number of occurrences of value.

        """
        return self._data.count(value)


class UserMutableSequence(
    MutableSequence[_T], UserSequence[_T]
):  # pylint: disable=too-many-ancestors
    """UserMutableSequence is a user-defined wrapper around mutable sequence objects."""

    _data: MutableSequence[_T]

    _repr_type = ReprType.SEQUENCE

    @overload
    def __getitem__(self, index: int) -> _T:
        ...

    @overload
    def __getitem__(self, index: slice) -> MutableSequence[_T]:
        ...

    def __getitem__(self, index: Union[int, slice]) -> Union[MutableSequence[_T], _T]:
        return self._data.__getitem__(index)

    @overload
    def __setitem__(self, index: int, value: _T) -> None:
        ...

    @overload
    def __setitem__(self, index: slice, value: Iterable[_T]) -> None:
        ...

    def __setitem__(self, index: Union[int, slice], value: Union[_T, Iterable[_T]]) -> None:
        # https://github.com/python/mypy/issues/7858
        self._data.__setitem__(index, value)  # type: ignore[index, assignment]

    def __delitem__(self, index: Union[int, slice]) -> None:
        self._data.__delitem__(index)

    def __iadd__(self, value: Iterable[_T]) -> MutableSequence[_T]:
        return self._data.__iadd__(value)

    def insert(self, index: int, value: _T) -> None:
        """Insert object before index.

        Arguments:
            index: Position of the mutable sequence.
            value: Element to be inserted into the mutable sequence.

        """
        self._data.insert(index, value)

    def append(self, value: _T) -> None:
        """Append object to the end of the mutable sequence.

        Arguments:
            value: Element to be appended to the mutable sequence.

        """
        self._data.append(value)

    def clear(self) -> None:
        """Remove all items from the mutable sequence."""
        self._data.clear()

    def extend(self, values: Iterable[_T]) -> None:
        """Extend mutable sequence by appending elements from the iterable.

        Arguments:
            values: Elements to be Extended into the mutable sequence.

        """
        self._data.extend(values)

    def reverse(self) -> None:
        """Reverse the items of the mutable sequence in place."""
        self._data.reverse()

    def pop(self, index: int = -1) -> _T:
        """Return the item at index (default last) and remove it from the mutable sequence.

        Arguments:
            index: Position of the mutable sequence.

        Returns:
            Element to be removed from the mutable sequence.

        """
        return self._data.pop(index)

    def remove(self, value: _T) -> None:
        """Remove the first occurrence of value.

        Arguments:
            value: Element to be removed from the mutable sequence.

        """
        self._data.remove(value)


class UserMapping(Mapping[_K, _V], ReprMixin):  # pylint: disable=too-many-ancestors
    """UserMapping is a user-defined wrapper around mapping objects."""

    _data: Mapping[_K, _V]

    _repr_type = ReprType.MAPPING

    def __len__(self) -> int:
        return self._data.__len__()

    def __getitem__(self, key: _K) -> _V:
        return self._data.__getitem__(key)

    def __contains__(self, key: object) -> bool:
        return self._data.__contains__(key)

    def __iter__(self) -> Iterator[_K]:
        return self._data.__iter__()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self._data.__eq__(other._data)

    @overload
    def get(self, key: _K) -> Optional[_V]:  # pylint: disable=arguments-differ
        ...

    @overload
    def get(self, key: _K, default: Union[_V, _T] = ...) -> Union[_V, _T]:
        ...

    def get(self, key: _K, default: Any = None) -> Any:
        """Return the value for the key if it is in the dict, else default.

        Arguments:
            key: The key for dict, which can be any immutable type.
            default: The value to be returned if key is not in the dict.

        Returns:
            The value for the key if it is in the dict, else default.

        """
        return self._data.get(key, default)

    def items(self) -> AbstractSet[Tuple[_K, _V]]:
        """Return a new view of the (key, value) pairs in dict.

        Returns:
            The (key, value) pairs in dict.

        """
        return self._data.items()

    def keys(self) -> AbstractSet[_K]:
        """Return a new view of the keys in dict.

        Returns:
            The keys in dict.

        """
        return self._data.keys()

    def values(self) -> ValuesView[_V]:
        """Return a new view of the values in dict.

        Returns:
            The values in dict.

        """
        return self._data.values()


class UserMutableMapping(
    MutableMapping[_K, _V], UserMapping[_K, _V]
):  # pylint: disable=too-many-ancestors
    """UserMutableMapping is a user-defined wrapper around mutable mapping objects."""

    __marker = object()

    _data: MutableMapping[_K, _V]

    def __setitem__(self, key: _K, value: _V) -> None:
        self._data.__setitem__(key, value)

    def __delitem__(self, key: _K) -> None:
        self._data.__delitem__(key)

    def clear(self) -> None:
        """Remove all items from the mutable mapping object."""
        self._data.clear()

    @overload
    def pop(self, key: _K) -> _V:  # pylint: disable=arguments-differ
        ...

    @overload
    def pop(self, key: _K, default: Union[_V, _T] = ...) -> Union[_V, _T]:
        ...

    def pop(self, key: _K, default: Any = __marker) -> Any:
        """Remove specified item and return the corresponding value.

        Arguments:
            key: The key for dict, which can be any immutable type.
            default: The value to be returned if the key is not in the dict and it is given.

        Returns:
            Value to be removed from the mutable mapping object.

        """
        if default is self.__marker:
            return self._data.pop(key)

        return self._data.pop(key, default)

    def popitem(self) -> Tuple[_K, _V]:
        """Remove and return a (key, value) pair as a tuple.

        Pairs are returned in LIFO (last-in, first-out) order.

        Returns:
            A (key, value) pair as a tuple.

        """
        return self._data.popitem()

    def setdefault(self, key: _K, default: _V = None) -> _V:  # type: ignore[assignment]
        """Set the value of the item with the specified key.

        If the key is in the dict, return the corresponding value.
        If not, insert the key with a value of default and return default.

        Arguments:
            key: The key for dict, which can be any immutable type.
            default: The value to be set if the key is not in the dict.

        Returns:
            The value for key if it is in the dict, else default.

        """
        return self._data.setdefault(key, default)

    @overload
    def update(  # pylint: disable=arguments-differ
        self, __m: Mapping[_K, _V], **kwargs: _V
    ) -> None:
        ...

    @overload
    def update(  # pylint: disable=arguments-differ
        self, __m: Iterable[Tuple[_K, _V]], **kwargs: _V
    ) -> None:
        ...

    @overload
    def update(self, **kwargs: _V) -> None:  # pylint: disable=arguments-differ,signature-differs
        ...

    def update(self, __m: Any = (), **kwargs: _V) -> None:  # pylint: disable=arguments-differ
        """Update the dict.

        Arguments:
            __m: A dict object, a generator object yielding a (key, value) pair
                or other object which has a `.keys()` method.
            **kwargs: The value to be added to the mutable mapping.

        """
        self._data.update(__m, **kwargs)
