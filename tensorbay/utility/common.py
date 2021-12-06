#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Common tools."""


from collections import defaultdict
from contextlib import contextmanager
from functools import wraps
from multiprocessing import Manager
from threading import Lock
from typing import Any, Callable, DefaultDict, Dict, Iterator, Sequence, Type, TypeVar, Union

import numpy as np

_T = TypeVar("_T")
_CallableWithoutReturnValue = TypeVar("_CallableWithoutReturnValue", bound=Callable[..., None])

MatrixType = Union[Sequence[Sequence[float]], np.ndarray]


def common_loads(object_class: Type[_T], contents: Any) -> _T:
    """A common method for loading an object from a dict or a list of dict.

    Arguments:
        object_class: The class of the object to be loaded.
        contents: The information of the object in a dict or a list of dict.

    Returns:
        The loaded object.

    """
    obj: _T = object.__new__(object_class)
    obj._loads(contents)  # type: ignore[attr-defined]  # pylint: disable=protected-access
    return obj


class EqMixin:
    """A mixin class to support __eq__() method.

    The __eq__() method defined here compares all the instance variables.

    """

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self.__dict__ == other.__dict__


@contextmanager
def _acquire(lock: Lock) -> Iterator[bool]:
    acquire = lock.acquire(blocking=False)
    yield acquire
    if not acquire:
        lock.acquire()
    lock.release()


thread_locks: DefaultDict[int, Lock] = defaultdict(Lock)


def locked(func: _CallableWithoutReturnValue) -> _CallableWithoutReturnValue:
    """The decorator to add threading lock for methods.

    Arguments:
        func: The method needs to add threading lock.

    Returns:
        The method with theading locked.

    """

    @wraps(func)
    def wrapper(self: Any, *arg: Any, **kwargs: Any) -> None:
        key = id(self)
        lock = thread_locks[key]
        with _acquire(lock) as success:
            if success:
                func(self, *arg, **kwargs)
                del thread_locks[key]

    return wrapper  # type: ignore[return-value]


class ProcessLocked:  # pylint: disable=too-few-public-methods
    """A decorator to add lock for methods called from different processes.

    Arguments:
        attr_name: The name of the attr to be taken as the key of the lock.

    """

    _manager = Manager()

    process_locks: Dict[str, Lock] = _manager.dict()

    def __init__(self, attr_name: str) -> None:
        self._attr_name = attr_name

    def __call__(self, func: _CallableWithoutReturnValue) -> _CallableWithoutReturnValue:
        """Return the locked function.

        Arguments:
            func: The function to add lock.

        Returns:
            The locked function.

        """

        @wraps(func)
        def wrapper(func_self: Any, *arg: Any, **kwargs: Any) -> None:
            key = getattr(func_self, self._attr_name)
            # https://github.com/PyCQA/pylint/issues/3313
            lock = self.process_locks.setdefault(
                key, self._manager.Lock()  # pylint: disable=no-member
            )

            with _acquire(lock) as success:
                if success:
                    func(func_self, *arg, **kwargs)
                    del self.process_locks[key]

        return wrapper  # type: ignore[return-value]
