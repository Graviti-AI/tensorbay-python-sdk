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


class UserSequence(Sequence[_T], ReprMixin):
    """UserSequence is a user-defined wrapper around sequence objects."""

    _data: Sequence[_T]

    _repr_type = ReprType.SEQUENCE

    @overload
    def __getitem__(self, index: int) -> _T:
        ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[_T]:
        ...

    def __getitem__(self, index: Union[int, slice]) -> Union[Sequence[_T], _T]:
        return self._data.__getitem__(index)

    def __len__(self) -> int:
        return self._data.__len__()

    def index(self, value: _T, start: int = 0, end: int = -1) -> int:
        """Return the first index of the value.

        Arguments:
            value: The value to be found.
            start: The start index of the subsequence.
            end: The end index of the subsequence.

        Returns:
            The First index of value.

        """
        return self._data.index(value, start, end)

    def count(self, value: _T) -> int:
        """Return the number of occurrences of value.

        Arguments:
            value: The value to be counted the number of occurrences.

        Returns:
            The number of occurrences of value.

        """
        return self._data.count(value)


class UserMutableSequence(MutableSequence[_T], ReprMixin):
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

    def __len__(self) -> int:
        return self._data.__len__()

    def __delitem__(self, index: Union[int, slice]) -> None:
        self._data.__delitem__(index)

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

    def extend(self, value: Iterable[_T]) -> None:
        """Extend mutable sequence by appending elements from the iterable.

        Arguments:
            value: Elements to be Extended into the mutable sequence.

        """
        self._data.extend(value)

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

    def __iadd__(self, value: Iterable[_T]) -> MutableSequence[_T]:
        return self._data.__iadd__(value)


class UserMapping(Mapping[_K, _V], ReprMixin):
    """UserMapping is a user-defined wrapper around mapping objects."""

    _data: Mapping[_K, _V]

    _repr_type = ReprType.MAPPING

    def __getitem__(self, key: _K) -> _V:
        return self._data.__getitem__(key)

    @overload
    def get(self, key: _K) -> Optional[_V]:
        ...

    @overload
    def get(self, key: _K, default: Union[_V, _T] = ...) -> Union[_V, _T]:
        ...

    def get(self, key: _K, default: Any = None) -> Any:
        """Return the value for the key if it is in the dictionary, else default.

        Arguments:
            key: The key for dictionary, which can be any immutable type.
            default: The value to be returned if key is not in the dictionary.

        Returns:
            The value for the key if it is in the dictionary, else default.

        """
        return self._data.get(key, default)

    def items(self) -> AbstractSet[Tuple[_K, _V]]:
        """Return a new view of the (key, value) pairs in dictionary.

        Returns:
            The (key, value) pairs in dictionary.

        """
        return self._data.items()

    def keys(self) -> AbstractSet[_K]:
        """Return a new view of the keys in dictionary.

        Returns:
            The keys in dictionary.

        """
        return self._data.keys()

    def values(self) -> ValuesView[_V]:
        """Return a new view of the values in dictionary.

        Returns:
            The values in dictionary.

        """
        return self._data.values()

    def __contains__(self, key: object) -> bool:
        return self._data.__contains__(key)

    def __iter__(self) -> Iterator[_K]:
        return self._data.__iter__()

    def __len__(self) -> int:
        return self._data.__len__()


class UserMutableMapping(UserMapping[_K, _V], MutableMapping[_K, _V]):
    """UserMutableMapping is a user-defined wrapper around mutable mapping objects."""

    _data: MutableMapping[_K, _V]
    __marker = object()

    def __setitem__(self, key: _K, value: _V) -> None:
        self._data.__setitem__(key, value)

    def __delitem__(self, key: _K) -> None:
        self._data.__delitem__(key)

    def clear(self) -> None:
        """Remove all items from the mutable mapping object."""
        self._data.clear()

    @overload
    def pop(self, key: _K) -> _V:
        ...

    @overload
    def pop(self, key: _K, default: Union[_V, _T] = ...) -> Union[_V, _T]:
        ...

    def pop(self, key: _K, default: Any = __marker) -> Any:
        """Remove specified item and return the corresponding value.

        Arguments:
            key: The key for dictionary, which can be any immutable type.
            default: The value to be returned if the key is not in the dictionary and it is given.

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

        If the key is in the dictionary, return the corresponding value.
        If not, insert the key with a value of default and return default.

        Arguments:
            key: The key for dictionary, which can be any immutable type.
            default: The value to be set if the key is not in the dictionary.

        Returns:
            The value for key if it is in the dictionary, else default.

        """
        return self._data.setdefault(key, default)

    @overload
    def update(self, __m: Mapping[_K, _V], **kwargs: _V) -> None:
        ...

    @overload
    def update(self, __m: Iterable[Tuple[_K, _V]], **kwargs: _V) -> None:
        ...

    @overload
    def update(self, **kwargs: _V) -> None:
        ...

    def update(self, __m: Any = None, **kwargs: _V) -> None:
        """Update the dictionary.

        Arguments:
            __m: A dictionary object, a generator object yielding a (key, value) pair
                or other object which has a `.keys()` method.
            **kwargs: The value to be added to the mutable mapping.

        """
        self._data.update(__m, **kwargs)
