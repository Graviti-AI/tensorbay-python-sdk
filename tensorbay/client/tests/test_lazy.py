#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#


import pytest

from tensorbay.client.lazy import InitPage, LazyPage, PagingList

TOTAL_COUNT = 1000
MIDDLE = TOTAL_COUNT // 2
LIMIT = 128
LIST = list(range(TOTAL_COUNT))

VALID_INDICES = (TOTAL_COUNT - 1, MIDDLE, -1, 0)
INDICES = VALID_INDICES + (TOTAL_COUNT,)
SLICES_WITHOUT_STEP = (
    slice(-1, 0),
    slice(-MIDDLE, -1),
    slice(0, MIDDLE),
    slice(0, TOTAL_COUNT - 1),
)
SLICES = SLICES_WITHOUT_STEP + (slice(0, TOTAL_COUNT, MIDDLE),)


def gen(offset, limit):
    stop = offset + limit
    if stop >= TOTAL_COUNT:
        stop = TOTAL_COUNT
    yield from range(offset, stop)
    return TOTAL_COUNT


class TestPagingList:
    def test_init(self):
        paging_list = PagingList(gen, LIMIT)
        assert not hasattr(paging_list, "_items")
        assert paging_list._func is gen
        assert paging_list._limit == LIMIT
        assert list(paging_list) == LIST

    def test_len(self):
        paging_list = PagingList(gen, LIMIT)
        assert len(paging_list) == TOTAL_COUNT

    def test_getitem(self):
        paging_list = PagingList(gen, LIMIT)
        for index in VALID_INDICES:
            assert paging_list[index] == LIST[index]

        with pytest.raises(IndexError):
            paging_list[TOTAL_COUNT]

        for slicing in SLICES_WITHOUT_STEP:
            assert list(paging_list[slicing]) == LIST[slicing]

    def test_setitem(self):
        paging_list = PagingList(gen, LIMIT)
        target = LIST.copy()

        for index in VALID_INDICES:
            paging_list[index] = -1
            target[index] = -1
            assert list(paging_list) == target

        with pytest.raises(IndexError):
            paging_list[TOTAL_COUNT] = -1

        for slicing in SLICES_WITHOUT_STEP:
            paging_list[slicing] = [-1, -1, -1, -1]
            target[slicing] = [-1, -1, -1, -1]
            assert list(paging_list) == target

        paging_list = PagingList(gen, LIMIT)
        target = LIST.copy()

        slicing = slice(0, TOTAL_COUNT, MIDDLE)
        with pytest.raises(ValueError):
            paging_list[slicing] = [-1]

        paging_list[slicing] = [-1, -1]
        target[slicing] = [-1, -1]
        assert list(paging_list) == target

    def test_delitem(self):
        paging_list = PagingList(gen, LIMIT)
        target = LIST.copy()

        for index in VALID_INDICES:
            del paging_list[index]
            del target[index]
            assert list(paging_list) == target

        with pytest.raises(IndexError):
            del paging_list[TOTAL_COUNT]

        for slicing in SLICES:
            del paging_list[slicing]
            del target[slicing]
            assert list(paging_list) == target

    def test_iter(self):
        paging_list = PagingList(gen, LIMIT)
        iterator = iter(paging_list)
        for i in LIST:
            assert next(iterator) == i

        with pytest.raises(StopIteration):
            next(iterator)

    def test_reversed(self):
        paging_list = PagingList(gen, LIMIT)
        assert list(reversed(LIST)) == list(reversed(paging_list))

    def test_contains(self):
        paging_list = PagingList(gen, LIMIT)
        for i in LIST[:: TOTAL_COUNT // 10]:
            assert i in paging_list

        assert LIST[-1] + 1 not in paging_list

    def test_iadd(self):
        paging_list = PagingList(gen, LIMIT)
        target = LIST.copy()

        paging_list += (1, 2, 3)
        target += (1, 2, 3)
        assert list(paging_list) == target

        paging_list.extend([])
        target.extend([])
        assert list(paging_list) == target

    def test_range(self):
        assert list(PagingList._range(10, 3)) == [(0, 3), (3, 3), (6, 3), (9, 1)]
        assert list(PagingList._range(0, 3)) == []
        assert list(PagingList._range(3, 10)) == [(0, 3)]

    @pytest.mark.parametrize("index", INDICES)
    def test_init_all_items(self, index):
        paging_list = PagingList(gen, LIMIT)

        paging_list._init_all_items(index)
        assert len(paging_list._items) == TOTAL_COUNT

        index = index if index >= 0 else 0
        start = index // LIMIT * LIMIT
        stop = start + LIMIT

        for i, item in enumerate(paging_list._items):
            if start <= i < stop:
                assert item.data == LIST[i]
                assert isinstance(item.page, InitPage)
            else:
                assert not hasattr(item, "data")
                assert isinstance(item.page, LazyPage)

    @pytest.mark.parametrize("slicing", SLICES)
    def test_init_sliced_items(self, slicing):
        paging_list = PagingList(gen, LIMIT)
        parent = PagingList(gen, LIMIT)

        paging_list._init_sliced_items(parent, slicing)
        assert paging_list._items == parent._items[slicing]

    @pytest.mark.parametrize("index", INDICES)
    def test_get_items(self, index):
        paging_list = PagingList(gen, LIMIT)

        for _ in range(2):
            items = paging_list._get_items(index)
            assert paging_list._items is items
            assert len(items) == TOTAL_COUNT

    @pytest.mark.parametrize("slicing", SLICES)
    def test_get_slice(self, slicing):
        paging_list = PagingList(gen, LIMIT)

        sliced_paging_list = paging_list._get_slice(slicing)
        assert not hasattr(sliced_paging_list, "_items")
        assert sliced_paging_list._init_items is not sliced_paging_list._init_all_items

        paging_list._init_all_items()

        sliced_paging_list = paging_list._get_slice(slicing)
        assert sliced_paging_list._items == paging_list._items[slicing]
        assert sliced_paging_list._init_items is not sliced_paging_list._init_all_items

    @pytest.mark.parametrize("index", INDICES)
    def test_insert(self, index):
        paging_list = PagingList(gen, LIMIT)
        target = LIST.copy()

        paging_list.insert(index, -1)
        target.insert(index, -1)
        assert list(paging_list) == target

    def test_append(self):
        paging_list = PagingList(gen, LIMIT)
        target = LIST.copy()

        for _ in range(10):
            paging_list.append(-1)
            target.append(-1)
            assert list(paging_list) == target

    def test_reverse(self):
        paging_list = PagingList(gen, LIMIT)
        target = LIST.copy()

        paging_list.reverse()
        target.reverse()

        assert list(paging_list) == target

    def test_pop(self):
        paging_list = PagingList(gen, LIMIT)
        target = LIST.copy()

        for index in VALID_INDICES:
            assert paging_list.pop(index) == target.pop(index)
            assert list(paging_list) == target

        with pytest.raises(IndexError):
            paging_list.pop(TOTAL_COUNT)

    def test_index(self):
        paging_list = PagingList(gen, LIMIT)

        for i in LIST[:: TOTAL_COUNT // 10]:
            assert paging_list.index(i) == LIST.index(i)

        for i in LIST[MIDDLE :: TOTAL_COUNT // 10]:
            assert paging_list.index(i, MIDDLE) == LIST.index(i, MIDDLE)

        for i in LIST[: MIDDLE : TOTAL_COUNT // 10]:
            assert paging_list.index(i, 0, MIDDLE) == LIST.index(i, 0, MIDDLE)

        for i in LIST[LIMIT : MIDDLE : TOTAL_COUNT // 10]:
            assert paging_list.index(i, LIMIT, MIDDLE) == LIST.index(i, LIMIT, MIDDLE)

        with pytest.raises(ValueError):
            assert paging_list.index(-1)

        with pytest.raises(ValueError):
            assert paging_list.index(LIST[100], 1000)

        with pytest.raises(ValueError):
            assert paging_list.index(LIST[100], stop=90)

        with pytest.raises(ValueError):
            assert paging_list.index(LIST[100], 110, 200)

    def test_count(self):
        paging_list = PagingList(gen, LIMIT)

        for i in LIST[:: TOTAL_COUNT // 10]:
            assert paging_list.count(i) == LIST.count(i)

        assert paging_list.count(-1) == LIST.count(-1)

    def test_extend(self):
        paging_list = PagingList(gen, LIMIT)
        target = LIST.copy()

        paging_list.extend([1, 2, 3])
        target.extend([1, 2, 3])
        assert list(paging_list) == target

        paging_list.extend([])
        target.extend([])
        assert list(paging_list) == target
