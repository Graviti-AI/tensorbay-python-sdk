#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Common_loads method, EqMixin class.

:meth:`common_loads` is a common method for loading an object from a dict or a list of dict.

:class:`EqMixin` is a mixin class to support __eq__() method,
which compares all the instance variables.

"""

from typing import Any, Type, TypeVar

_T = TypeVar("_T")


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


class EqMixin:  # pylint: disable=too-few-public-methods
    """A mixin class to support __eq__() method.

    The __eq__() method defined here compares all the instance variables.

    """

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self.__dict__ == other.__dict__
