#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Lazy evaluation related classes."""

from itertools import repeat, zip_longest
from typing import (
    Any,
    Callable,
    Generator,
    Generic,
    Iterable,
    Iterator,
    List,
    MutableSequence,
    Optional,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from ..utility import ReprMixin, ReprType, locked

_T = TypeVar("_T")
PagingGenerator = Callable[[int, int], Generator[_T, None, int]]


class LazyItem(Generic[_T]):
    """In paging lazy evaluation system, a LazyItem instance represents an element in a pagination.

    If user wants to access the elememt, LazyItem will trigger the paging request to pull a page of
    elements and return the required element. All the pulled elements will be stored in different
    LazyItem instances and will not be requested again.

    Arguments:
        page: The page the item belongs to.

    Attributes:
        page: The parent :class:`LazyPage` of this item.
        data: The actual element stored in this item.

    """

    _S = TypeVar("_S", bound="LazyItem[_T]")

    __slots__ = ("page", "data")

    def __init__(self, page: "LazyPage[_T]", data: _T):
        self.page = page
        self.data = data

    @classmethod
    def from_page(cls, page: "LazyPage[_T]") -> "LazyItem[_T]":
        """Create a LazyItem instance from page.

        Arguments:
            page: The page of the element.

        Returns:
            The LazyItem instance which stores the input page.

        """
        obj: "LazyItem[_T]" = object.__new__(cls)
        obj.page = page
        return obj

    @classmethod
    def from_data(cls, data: _T) -> "LazyItem[_T]":
        """Create a LazyItem instance from data.

        Arguments:
            data: The actual data needs to be stored in LazyItem.

        Returns:
            The LazyItem instance which stores the input data.

        """
        obj: "LazyItem[_T]" = object.__new__(cls)
        obj.data = data
        return obj

    def get(self) -> _T:
        """Access the actual element represented by LazyItem.

        If the element is already pulled from web, it will be return directly, otherwise this
        function will request for a page of elements to get the required elememt.

        Returns:
            The actual element this LazyItem instance represents.

        """
        if not hasattr(self, "data"):
            self.page.pull()

        return self.data


_R = TypeVar("_R")


class ReturnGenerator(Generic[_T, _R]):
    """ReturnGenerator is a generator wrap to get the return value easily.

    Arguments:
        generator: The generator needs to be wrapped.

    Attributes:
        value: The return value of the input generator.

    """

    value: _R

    def __init__(self, generator: Generator[_T, Any, _R]):
        self._generator = generator

    def __iter__(self) -> Iterator[_T]:
        self.value = yield from self._generator


class LazyPage(Generic[_T]):
    """In paging lazy evaluation system, a LazyPage instance represents a page with elements.

    LazyPage is used for sending paging request to pull a page of elements and storing them in
    different :class:`LazyItem` instances.

    Arguments:
        offset: The offset of the page.
        limit: The limit of the page.
        func: A paging generator function, which takes offset<int> and limit<int> as inputs and
            returns a generator. The returned generator should yield the element user needs, and
            return the total count of the elements in the paging request.

    Attributes:
        items: The :class:`LazyItem` list which represents a page of elements.

    """

    __slots__: Tuple[str, ...] = ("_offset", "_limit", "_func", "items")

    def __init__(self, offset: int, limit: int, func: PagingGenerator[_T]) -> None:
        self.items: Tuple[LazyItem[_T], ...] = tuple(LazyItem.from_page(self) for _ in range(limit))

        self._init(offset, limit, func)

    def _init(self, offset: int, limit: int, func: PagingGenerator[_T]) -> None:
        self._offset = offset
        self._limit = limit
        self._func = func

    @locked
    def pull(self) -> None:
        """Send paging request to pull a page of elements and store them in :class:`LazyItem`."""
        for data, item in zip(self._func(self._offset, self._limit), self.items):
            item.data = data


class InitPage(LazyPage[_T]):
    """In paging lazy evaluation system, InitPage is the page for initializing :class:`PagingList`.

    InitPage will send a paging request to pull a page of elements and storing them in different
    :class:`LazyItem` instances when construction. And the totalCount of the page will also be
    stored in the instance.

    Arguments:
        offset: The offset of the page.
        limit: The limit of the page.
        func: A paging generator function, which takes offset<int> and limit<int> as inputs and
            returns a generator. The returned generator should yield the element user needs, and
            return the total count of the elements in the paging request.

    Attributes:
        items: The :class:`LazyItem` list which represents a page of elements.
        total_count: The totalCount of the paging request.

    """

    __slots__ = LazyPage.__slots__ + ("total_count",)

    def __init__(  # pylint: disable=super-init-not-called
        self, offset: int, limit: int, func: PagingGenerator[_T]
    ) -> None:
        generator = ReturnGenerator(func(offset, limit))
        self.items: Tuple[LazyItem[_T], ...] = tuple(LazyItem(self, data) for data in generator)

        self._init(offset, len(self.items), func)

        self.total_count = generator.value


class PagingList(MutableSequence[_T], ReprMixin):  # pylint: disable=too-many-ancestors
    """PagingList is a wrap of web paging request.

    It follows the python MutableSequence protocal, which means it can be used like a python builtin
    list. And it provides features like lazy evaluation and cache.

    Arguments:
        func: A paging generator function, which takes offset<int> and limit<int> as inputs and
            returns a generator. The returned generator should yield the element user needs, and
            return the total count of the elements in the paging request.
        limit: The page size of each paging request.

    """

    _S = TypeVar("_S", bound="PagingList[_T]")

    _repr_type = ReprType.SEQUENCE

    _items: List[LazyItem[_T]]

    def __init__(self, func: PagingGenerator[_T], limit: int) -> None:
        self._func = func
        self._limit = limit
        self._init_items: Callable[[int], None] = self._init_all_items

    def __len__(self) -> int:
        return self._get_items().__len__()

    @overload
    def __getitem__(self, index: int) -> _T:
        ...

    @overload
    def __getitem__(self: _S, index: slice) -> _S:
        ...

    def __getitem__(self: _S, index: Union[int, slice]) -> Union[_T, _S]:
        if isinstance(index, slice):
            return self._get_slice(index)

        return self._get_items(index)[index].get()

    @overload
    def __setitem__(self, index: int, value: _T) -> None:
        ...

    @overload
    def __setitem__(self, index: slice, value: Iterable[_T]) -> None:
        ...

    def __setitem__(self, index: Union[int, slice], value: Union[_T, Iterable[_T]]) -> None:
        # https://github.com/python/mypy/issues/7858
        if isinstance(index, slice):
            self._get_items().__setitem__(
                index,
                map(LazyItem.from_data, value),  # type: ignore[arg-type]
            )
            return

        self._get_items(index).__setitem__(
            index,
            LazyItem.from_data(value),  # type: ignore[arg-type]
        )

    def __delitem__(self, index: Union[int, slice]) -> None:
        self._get_items().__delitem__(index)

    def __iter__(self) -> Iterator[_T]:
        for item in self._get_items():
            yield item.get()

    def __reversed__(self) -> Iterator[_T]:
        for item in self._get_items().__reversed__():
            yield item.get()

    def __contains__(self, value: Any) -> bool:
        for item in self._get_items():
            if item.get() == value:
                return True

        return False

    def __iadd__(self: _S, values: Iterable[_T]) -> _S:
        self._get_items().__iadd__(LazyItem.from_data(value) for value in values)
        return self

    @staticmethod
    def _range(total_count: int, limit: int) -> Iterator[Tuple[int, int]]:
        """A Generator which generates offset and limit for paging request.

        Examples:
            >>> self._range(10, 3)
            <generator object paging_range at 0x11b9932e0>

            >>> list(self._range(10, 3))
            [(0, 3), (3, 3), (6, 3), (9, 1)]

        Arguments:
            total_count: The total count of the page.
            limit: The paging limit.

        Yields:
            The tuple (offset, limit) for paging request.

        """
        div, mod = divmod(total_count, limit)
        yield from zip_longest(range(0, total_count, limit), repeat(limit, div), fillvalue=mod)

    @locked
    def _init_all_items(self, index: int = 0) -> None:
        index = index if index >= 0 else 0
        index_offset = index // self._limit * self._limit
        init_page = InitPage(index_offset, self._limit, self._func)
        total_count = init_page.total_count
        self._items: List[LazyItem[_T]] = []
        for offset, limit in self._range(total_count, self._limit):
            page = init_page if offset == index_offset else LazyPage(offset, limit, self._func)
            self._items.extend(page.items)

    @locked
    def _init_sliced_items(self: _S, parent: _S, slicing: slice) -> None:
        self._items = parent._get_items()[slicing]  # pylint: disable=protected-access

    def _get_items(self, index: int = 0) -> List[LazyItem[_T]]:
        if not hasattr(self, "_items"):
            self._init_items(index)

        return self._items

    def _get_slice(self: _S, slicing: slice) -> _S:
        # pylint: disable=protected-access
        paging_list = self.__class__(self._func, self._limit)
        if hasattr(self, "_items"):
            paging_list._items = self._items[slicing]
        else:
            paging_list._init_items = lambda _: paging_list._init_sliced_items(self, slicing)

        return paging_list

    def insert(self, index: int, value: _T) -> None:
        """Insert object before index.

        Arguments:
            index: Position of the PagingList.
            value: Element to be inserted into the PagingList.

        """
        self._get_items(index).insert(index, LazyItem.from_data(value))

    def append(self, value: _T) -> None:
        """Append object to the end of the PagingList.

        Arguments:
            value: Element to be appended to the PagingList.

        """
        self._get_items().append(LazyItem.from_data(value))

    def reverse(self) -> None:
        """Reverse the items of the PagingList in place."""
        self._get_items().reverse()

    def pop(self, index: int = -1) -> _T:
        """Return the item at index (default last) and remove it from the PagingList.

        Arguments:
            index: Position of the PagingList.

        Returns:
            Element to be removed from the PagingList.

        """
        return self._get_items(index).pop(index).get()

    def index(self, value: Any, start: int = 0, stop: Optional[int] = None) -> int:
        """Return the first index of the value.

        Arguments:
            value: The value to be found.
            start: The start index of the subsequence.
            stop: The end index of the subsequence.

        Raises:
            ValueError: When the value is not in the PagingList

        Returns:
            The first index of the value.


        """
        items = self._get_items(start)
        length = len(items)

        stop = length if stop is None else min(stop, length)

        for i in range(start, stop):
            if items[i].get() == value:
                return i

        raise ValueError(f"{value} is not in PagingList")

    def count(self, value: Any) -> int:
        """Return the number of occurrences of value.

        Arguments:
            value: The value needs to be counted.

        Returns:
            The number of occurrences of value.

        """
        return sum(1 for item in self._get_items() if item.get() == value)

    def extend(self, values: Iterable[_T]) -> None:
        """Extend PagingList by appending elements from the iterable.

        Arguments:
            values: Elements to be extended into the PagingList.

        """
        self._get_items().extend(LazyItem.from_data(value) for value in values)
