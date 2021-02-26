#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Common_loads method.

Common_loads is a common method for loading an object from a dict or a list of dict.

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
