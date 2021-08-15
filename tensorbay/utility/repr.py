#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""ReprType and ReprMixin.

:class:`ReprType` is an enumeration type, which defines the repr strategy type and includes
'INSTANCE', 'SEQUENCE', 'MAPPING'.

:class:`ReprMixin` provides customized repr config and method.

"""

from abc import ABC
from enum import Enum, auto
from typing import Any, Callable, Dict, Iterable, Mapping, Sequence, Tuple, Type, TypeVar, Union


class ReprType(Enum):
    """ReprType is an enumeration type.

    It defines the repr strategy type and includes 'INSTANCE', 'SEQUENCE' and 'MAPPING'.

    """

    INSTANCE = auto()
    SEQUENCE = auto()
    MAPPING = auto()


class ReprMixin:
    """ReprMixin provides customized repr config and method."""

    _repr_type = ReprType.INSTANCE
    _repr_attrs: Iterable[str] = ()
    _repr_maxlevel = 1
    _repr_non_empty = False

    def __repr__(self) -> str:
        return _repr1(self, self._repr_maxlevel, self._repr_maxlevel, True)

    def __str__(self) -> str:
        return _repr1(self, self._repr_maxlevel, self._repr_maxlevel, False)

    def _repr_head(self) -> str:
        return self.__class__.__name__


class _ReprConfig:
    """Config for customized repr method.

    Arguments:
        indent: The indent width for different level repr string.
        maxlist: The max items displayed in the sequence repr string.
        maxdict: The max items displayed in the mapping repr string.

    """

    def __init__(self, indent: int = 2, maxlist: int = 16, maxdict: int = 16) -> None:
        self.indent = indent
        self.maxlist = maxlist
        self.maxdict = maxdict

    @property
    def indent(self) -> int:
        """The getter of repr indent width.

        Returns:
            The indent width of repr config.

        """
        return self._indent

    @indent.setter
    def indent(self, indent: int) -> None:
        """The setter of repr indent width.

        Arguments:
            indent: The width of the ident to be set.

        """
        self._indent = indent
        self._indent_str = " " * indent


repr_config = _ReprConfig()


# Explicitly inherit from 'abc.ABC' to tell pylint it is a abstract class
# Reference:
# - https://github.com/PyCQA/pylint/issues/3098
# - https://github.com/PyCQA/pylint/pull/3446
class _ReprSequence(ReprMixin, Sequence[Any], ABC):
    ...


class _ReprMapping(ReprMixin, Mapping[Any, Any], ABC):  # pylint: disable=too-many-ancestors
    ...


_ReprPrinter = Callable[[Any, int, int, bool], str]

_PRINTERS: Dict[Union[Type[Any], ReprType], _ReprPrinter] = {}


class _PrinterRegister:
    """Decorator class to register repr printer functions to '_PRINTERS'.

    Arguments:
        key: The key of the '_PRINTERS' for repr dispatch.

    """

    _S = TypeVar("_S", bound=_ReprPrinter)

    def __init__(self, key: Union[Type[Any], ReprType]) -> None:
        self._key = key

    def __call__(self, printer: _S) -> _S:
        _PRINTERS[self._key] = printer
        return printer


def _repr1(obj: Any, level: int, maxlevel: int, folding: bool) -> str:
    """Customized repr method.

    Arguments:
        obj: The object need to be transferred to repr string.
        level: The current repr level.
        maxlevel: The max repr level.
        folding: Whether fold the "repr" of the object.

    Returns:
        "repr" of the object.

    """
    # pylint: disable=protected-access
    printer_key = obj._repr_type if hasattr(obj, "_repr_type") else type(obj)
    printer = _PRINTERS.get(printer_key, None)
    return printer(obj, level, maxlevel, folding) if printer else repr(obj)


@_PrinterRegister(ReprType.INSTANCE)
def _repr_instance(obj: ReprMixin, level: int, maxlevel: int, folding: bool) -> str:
    """Customized repr method for `ReprType.INSTANCE`.

    Arguments:
        obj: The object need to be transferred to repr string.
        level: The current repr level.
        maxlevel: The max repr level.
        folding: Whether fold the "repr" of the object.

    Returns:
        "repr" of the object.

    """
    # pylint: disable=protected-access
    return f"{obj._repr_head()}{_repr_attrs(obj, level, maxlevel, folding)}"


@_PrinterRegister(ReprType.SEQUENCE)
def _repr_sequence(obj: _ReprSequence, level: int, maxlevel: int, folding: bool) -> str:
    """Customized repr method for `ReprType.SEQUENCE`.

    Arguments:
        obj: The object need to be transferred to repr string.
        level: The current repr level.
        maxlevel: The max repr level.
        folding: Whether fold the "repr" of the object.

    Returns:
        "repr" of the object.

    """
    # pylint: disable=protected-access
    return (
        f"{obj._repr_head()} {_repr_builtin_list(obj, level, maxlevel, folding)}"
        f"{_repr_attrs(obj, level, maxlevel, folding)}"
    )


@_PrinterRegister(ReprType.MAPPING)
def _repr_mapping(obj: _ReprMapping, level: int, maxlevel: int, folding: bool) -> str:
    """Customized repr method for `ReprType.MAPPING`.

    Arguments:
        obj: The object need to be transferred to repr string.
        level: The current repr level.
        maxlevel: The max repr level.
        folding: Whether fold the "repr" of the object.

    Returns:
        "repr" of the object.

    """
    # pylint: disable=protected-access
    return (
        f"{obj._repr_head()} {_repr_builtin_dict(obj, level, maxlevel, folding)}"
        f"{_repr_attrs(obj, level, maxlevel, folding)}"
    )


@_PrinterRegister(list)
def _repr_builtin_list(obj: Sequence[Any], level: int, maxlevel: int, folding: bool) -> str:
    """Customized repr method for buildin type list.

    Arguments:
        obj: The object need to be transferred to repr string.
        level: The current repr level.
        maxlevel: The max repr level.
        folding: Whether fold the "repr" of the object.

    Returns:
        "repr" of the object.

    """
    return _repr_builtin_sequence(obj, level, maxlevel, folding, "[", "]")


@_PrinterRegister(tuple)
def _repr_builtin_tuple(obj: Sequence[Any], level: int, maxlevel: int, folding: bool) -> str:
    """Customized repr method for buildin type tuple.

    Arguments:
        obj: The object need to be transferred to repr string.
        level: The current repr level.
        maxlevel: The max repr level.
        folding: Whether fold the "repr" of the object.

    Returns:
        "repr" of the object.

    """
    return _repr_builtin_sequence(obj, level, maxlevel, folding, "(", ")")


@_PrinterRegister(dict)
def _repr_builtin_dict(obj: Mapping[Any, Any], level: int, maxlevel: int, folding: bool) -> str:
    """Customized repr method for buildin type dict.

    Arguments:
        obj: The object need to be transferred to repr string.
        level: The current repr level.
        maxlevel: The max repr level.
        folding: Whether fold the "repr" of the object.

    Returns:
        "repr" of the object.

    """
    if getattr(obj, "_repr_non_empty", False) and level <= 0:
        return "{...}"

    object_length = len(obj)
    if object_length == 0:
        return "{}"
    if level <= 0:
        return "{...}"
    newlevel = level - 1

    keys = tuple(obj)

    fold, unfold = _calculate_fold_number(object_length, repr_config.maxdict, folding)
    pieces = [
        f"{repr(key)}: {_repr1(obj[key], newlevel, maxlevel, folding)}" for key in keys[:unfold]
    ]
    if fold:
        key = keys[-1]
        pieces.append(f"... ({fold} items are folded)")
        pieces.append(f"{repr(key)}: {_repr1(obj[key], newlevel, maxlevel, folding)}")

    return _join_with_indent(pieces, level, maxlevel, "{", "}")


def _repr_attrs(obj: Any, level: int, maxlevel: int, folding: bool) -> str:
    """Customized repr method for object attributes.

    Arguments:
        obj: The object need to be transferred to repr string.
        level: The current repr level.
        maxlevel: The max repr level.
        folding: Whether fold the "repr" of the object.

    Returns:
        "repr" of the object.

    """
    # pylint: disable=protected-access
    if not obj._repr_attrs:
        return ""

    attributes = []
    for attribute in obj._repr_attrs:
        value = getattr(obj, attribute, ...)
        if value is not ...:
            attributes.append((attribute, value))

    if not attributes:
        return "()"

    if level <= 0:
        return "(...)"

    newlevel = level - 1
    pieces = (f"({key}): {_repr1(value, newlevel, maxlevel, folding)}" for key, value in attributes)

    return _join_with_indent(pieces, level, maxlevel, "(", ")")


def _repr_builtin_sequence(  # pylint: disable=too-many-arguments
    obj: Sequence[Any], level: int, maxlevel: int, folding: bool, left: str, right: str
) -> str:
    """Customized repr method for sequence.

    Arguments:
        obj: The object need to be transferred to repr string.
        level: The current repr level.
        maxlevel: The max repr level.
        folding: Whether fold the "repr" of the object.
        left: The left bracket symbol.
        right: The right bracket symbol.

    Returns:
        "repr" of the object.

    """
    if getattr(obj, "_repr_non_empty", False) and level <= 0:
        return f"{left}...{right}"

    object_length = len(obj)
    if object_length == 0:
        return f"{left}{right}"
    if level <= 0:
        return f"{left}...{right}"
    newlevel = level - 1

    fold, unfold = _calculate_fold_number(object_length, repr_config.maxlist, folding)
    pieces = [_repr1(item, newlevel, maxlevel, folding) for item in obj[:unfold]]
    if fold:
        pieces.append(f"... ({fold} items are folded)")
        pieces.append(_repr1(obj[-1], newlevel, maxlevel, folding))

    return _join_with_indent(pieces, level, maxlevel, left, right)


def _calculate_fold_number(length: int, max_length: int, folding: bool) -> Tuple[int, int]:
    """Calculate the number of the folded and unfolded items.

    Arguments:
        length: The object length.
        max_length: The configured max length.
        folding: Whether fold the "repr" of the object.

    Returns:
        The number of the folded items & the number of the unfolded items.

    """
    if folding and length > max_length:
        return length - max_length + 1, max_length - 2
    return 0, length


def _join_with_indent(
    pieces: Iterable[str], level: int, maxlevel: int, left: str, right: str
) -> str:
    """Handle the indent, newline and "," of the string list.

    Arguments:
        pieces: The string list need to be transferred to repr string.
        level: The current repr level.
        maxlevel: The max repr level.
        left: The left bracket symbol.
        right: The right bracket symbol.

    Returns:
        Repr string with indent, newline and ",".

    """
    # pylint: disable=protected-access
    inner_indent = repr_config._indent_str * (maxlevel - level + 1)
    outer_indent = repr_config._indent_str * (maxlevel - level)

    sep = f",\n{inner_indent}"
    return f"{left}\n{inner_indent}{sep.join(pieces)}\n{outer_indent}{right}"
