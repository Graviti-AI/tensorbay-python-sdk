#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Utility classes."""

from .attr import AttrsMixin, attr, attr_base, camel, upper
from .common import (
    DefaultValueDeprecated,
    Deprecated,
    EqMixin,
    KwargsDeprecated,
    MatrixType,
    common_loads,
    locked,
)
from .name import NamedList, NameMixin, NameSortedDict, NameSortedList
from .repr import ReprMixin, ReprType, repr_config
from .type import SubcatalogTypeRegister, TypeEnum, TypeMixin, TypeRegister
from .user import UserMapping, UserMutableMapping, UserMutableSequence, UserSequence

__all__ = [
    "AttrsMixin",
    "DefaultValueDeprecated",
    "Deprecated",
    "EqMixin",
    "KwargsDeprecated",
    "MatrixType",
    "NameMixin",
    "NameSortedDict",
    "NameSortedList",
    "NamedList",
    "ReprMixin",
    "ReprType",
    "SubcatalogTypeRegister",
    "TypeEnum",
    "TypeMixin",
    "TypeRegister",
    "UserMapping",
    "UserMutableMapping",
    "UserMutableSequence",
    "UserSequence",
    "attr",
    "attr_base",
    "camel",
    "common_loads",
    "locked",
    "repr_config",
    "upper",
]
