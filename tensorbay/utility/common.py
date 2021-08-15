#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Common_loads method, EqMixin class.

:meth:`common_loads` is a common method for loading an object from a dict or a list of dict.

:class:`EqMixin` is a mixin class to support __eq__() method,
which compares all the instance variables.

"""

from collections import defaultdict
from functools import wraps
from threading import Lock
from typing import Any, Callable, DefaultDict, Sequence, Type, TypeVar, Union

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


locks: DefaultDict[int, Lock] = defaultdict(Lock)


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
        lock = locks[key]
        acquire = lock.acquire(blocking=False)
        try:
            if acquire:
                func(self, *arg, **kwargs)
                del locks[key]
            else:
                lock.acquire()
        finally:
            lock.release()

    return wrapper  # type: ignore[return-value]
