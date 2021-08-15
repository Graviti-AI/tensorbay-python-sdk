#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""TypeEnum, TypeMixin and TypeRegister.

:class:`TypeEnum` is a superclass for enumeration classes that need to create a mapping with class.

:class:`TypeMixin` is a superclass for the class which needs to link with :class:`TypeEnum`.

:class:`TypeRegister` is a decorator, which is used for registering
:class:`TypeMixin` to :class:`TypeEnum`.

"""

from enum import Enum
from typing import Any, Dict, Generic, Type, TypeVar


class TypeEnum(Enum):
    """TypeEnum is a superclass for enumeration classes that need to create a mapping with class.

    The 'type' property is used for getting the corresponding class of the enumeration.

    """

    __registry__: Dict["TypeEnum", Type[Any]] = {}

    def __init_subclass__(cls) -> None:
        cls.__registry__ = {}

    @property
    def type(self) -> Type[Any]:
        """Get the corresponding class.

        Returns:
            The corresponding class.

        """
        return self.__registry__[self]


_T = TypeVar("_T", bound=TypeEnum)


class TypeMixin(Generic[_T]):
    """TypeMixin is a superclass for the class which needs to link with TypeEnum.

    It provides the class variable 'TYPE' to access the corresponding TypeEnum.

    """

    _enum: _T

    @property
    def enum(self) -> _T:
        """Get the corresponding TypeEnum.

        Returns:
            The corresponding TypeEnum.

        """
        return self._enum


_S = TypeVar("_S", bound=TypeMixin[Any])


class TypeRegister(Generic[_T]):
    """TypeRegister is a decorator, which is used for registering TypeMixin to TypeEnum.

    Arguments:
        enum: The corresponding :class:`TypeEnum` of the :class:`TypeMixin`.

    """

    def __init__(self, enum: _T) -> None:
        self._enum = enum

    def __call__(self, class_: Type[_S]) -> Type[_S]:
        """Call the TypeRegister as a function.

        Arguments:
            class_: The :class:`TypeEnum` of the :class:`TypeMixin` to be registered.

        Returns:
            The :class:`TypeEnum` of the :class:`TypeMixin`.

        """
        class_._enum = self._enum
        self._enum.__registry__[self._enum] = class_
        return class_
