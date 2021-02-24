#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""This file defines class CatagoryInfo, AttributeInfo and Subcatalog."""

from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, TypeVar, Union

from ..utility import NameMixin, ReprMixin, common_loads

_AvailaleType = Union[list, bool, int, float, str, None]
_SingleArgType = Union[str, None, Type[_AvailaleType]]
_ArgType = Union[_SingleArgType, Iterable[_SingleArgType]]
_EnumElementType = Union[str, float, bool, None]


class _AttributeType(Enum):
    """All the possible type of the attributes."""

    array = list
    boolean = bool
    integer = int
    number = float
    string = str
    null = None
    instance = "instance"

    @classmethod
    def get_type_name(cls, type_: _SingleArgType) -> str:
        """Return the corresponding enumeration type name of the given string or type.

        Arguments:
            type_: A string or type indicating the attribute type.

        Returns:
            The name of the :class:`_AttributeType` object corresponding to the given type_.

        Raises:
            ValueError: When the input type_ is not supported.

        """
        if type_ in cls.__members__:
            return type_  # type: ignore[return-value]

        try:
            return cls(type_).name
        except ValueError as error:
            raise ValueError(
                "Invalid type_ values for attribute. "
                f"Only support {tuple(cls.__members__.keys())} attribute types"
            ) from error


class Items(ReprMixin):
    """The base class of :class:`AttributeInfo`, representing the item of an attribute.

    Arguments:
        enum: All the possible values of the attribute.
        type_: The type of the attribute value.
        minimum: The minimum value of number type attribute.
        maximum: The maximum value of number type attribute.
        items: The item inside array type attributes.

    Raises:
        TypeError: When both enum and type_ are absent or
            when type_ is array but items is absent.

    """

    _T = TypeVar("_T", bound="Items")
    _repr_attrs: Tuple[str, ...] = ("type", "enum", "minimum", "maximum", "items")

    def __init__(
        self: _T,
        *,
        type_: _ArgType = "",
        enum: Optional[Iterable[_EnumElementType]] = None,
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
        items: Optional["Items"] = None,
    ):
        if type_ != "":
            self.type, has_array = self._convert_type(type_)
            if has_array and items:
                self.items = items

        if enum:
            self.enum = list(enum)
        if minimum is not None:
            self.minimum = minimum
        if minimum is not None:
            self.maximum = maximum

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Load an Items from a dict containing the items information.

        Arguments:
            contents: A dict containing the information of an Items.

        Returns:
            The loaded Items.

        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:
        if "type" in contents:
            self.type, has_array = self._convert_type(contents["type"])
            if has_array:
                self.items = Items.loads(contents["items"])

        if "enum" in contents:
            self.enum = contents["enum"]

        if "minimum" in contents:
            self.minimum = contents["minimum"]

        if "maximum" in contents:
            self.maximum = contents["maximum"]

    @staticmethod
    def _convert_type(type_: _ArgType) -> Tuple[Union[str, List[str]], bool]:
        if isinstance(type_, Iterable) and not isinstance(type_, str):  # pylint: disable=W1116
            converted_types = [_AttributeType.get_type_name(single_type) for single_type in type_]
            return converted_types, "array" in converted_types

        converted_type = _AttributeType.get_type_name(type_)
        return converted_type, converted_type == "array"

    def dumps(self) -> Dict[str, Any]:
        """Dump the information of this item as a dictionary.

        Returns:
            A dictionary contains all information of this item.

        """
        contents: Dict[str, Any] = {}
        if hasattr(self, "type"):
            contents["type"] = self.type

        if hasattr(self, "items"):
            contents["items"] = self.items.dumps()

        if hasattr(self, "enum"):
            contents["enum"] = self.enum

        if hasattr(self, "minimum"):
            contents["minimum"] = self.minimum

        if hasattr(self, "maximum"):
            contents["maximum"] = self.maximum

        return contents


class AttributeInfo(NameMixin, Items):
    """Information of an attribute.

    :param name: The name of the attribute
    :param enum: All the possible values of the attribute.
    :param type_: The type of the attribute value.
    :param minimum: The minimum value of number type attribute.
    :param maximum: The maximum value of number type attribute.
    :param items: The item inside array type attributes.
    :param parent_categories: The parent categories of the attribute
    :param description: The description of the attribute
    """

    _T = TypeVar("_T", bound="AttributeInfo")
    _repr_attrs = ("name", "parent_categories") + Items._repr_attrs
    _repr_maxlevel = 2

    def __init__(
        self,
        name: str,
        *,
        type_: _ArgType = "",
        enum: Optional[Iterable[_EnumElementType]] = None,
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
        items: Optional[Items] = None,
        parent_categories: Union[None, str, Iterable[str]] = None,
        description: Optional[str] = None,
    ):
        NameMixin.__init__(self, name, description)
        Items.__init__(self, type_=type_, enum=enum, minimum=minimum, maximum=maximum, items=items)

        if not parent_categories:
            return

        if isinstance(parent_categories, str):
            self.parent_categories = [parent_categories]
        else:
            self.parent_categories = list(parent_categories)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Load an AttributeInfo from a dict containing the attribute information.

        :param contents: A dict containing the information of an AttributeInfo
        :return: The loaded AttributeInfo
        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:
        NameMixin._loads(self, contents)
        Items._loads(self, contents)

        if "parentCategories" in contents:
            self.parent_categories = contents["parentCategories"]

    def dumps(self) -> Dict[str, Any]:
        """Dumps the information of this attribute as a dictionary.

        :return: A dictionary contains all information of this attribute
        """
        contents: Dict[str, Any] = NameMixin.dumps(self)
        contents.update(Items.dumps(self))

        if hasattr(self, "parent_categories"):
            contents["parentCategories"] = self.parent_categories

        return contents
