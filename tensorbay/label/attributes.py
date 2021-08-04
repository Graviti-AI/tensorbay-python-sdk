#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Items and AttributeInfo.

:class:`AttributeInfo` represents the information of an attribute.
It refers to the `Json schema`_ method to describe an attribute.

:class:`Items` is the base class of :class:`AttributeInfo`, representing the items of an attribute.

.. _Json schema: https://json-schema.org/

"""

from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, TypeVar, Union

from ..utility import EqMixin, NameMixin, ReprMixin, attr, attr_base, camel, common_loads

_AvailaleType = Union[list, bool, int, float, str, None]
_SingleArgType = Union[str, None, Type[_AvailaleType]]
_ArgType = Union[_SingleArgType, Iterable[_SingleArgType]]
_EnumElementType = Union[str, float, bool, None]


class _AttributeType(Enum):
    """All the possible type of the attributes."""

    # pylint: disable=invalid-name
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


class Items(ReprMixin, EqMixin):
    """The base class of :class:`AttributeInfo`, representing the items of an attribute.

    When the value type of an attribute is array,
    the :class:`AttributeInfo` would contain an 'items' field.

    .. todo::
        The format of argument *type_* on the generated web page is incorrect.

    Arguments:
        type_: The type of the attribute value, could be a single type or multi-types.
            The type must be within the followings:

                - array
                - boolean
                - integer
                - number
                - string
                - null
                - instance

        enum: All the possible values of an enumeration attribute.
        minimum: The minimum value of number type attribute.
        maximum: The maximum value of number type attribute.
        items: The items inside array type attributes.

    Attributes:
        type: The type of the attribute value, could be a single type or multi-types.
        enum: All the possible values of an enumeration attribute.
        minimum: The minimum value of number type attribute.
        maximum: The maximum value of number type attribute.
        items: The items inside array type attributes.

    Raises:
        TypeError: When both ``enum`` and ``type_`` are absent or
            when ``type_`` is array and ``items`` is absent.

    Examples:
        >>> Items(type_="integer", enum=[1, 2, 3, 4, 5], minimum=1, maximum=5)
        Items(
          (type): 'integer',
          (enum): [...],
          (minimum): 1,
          (maximum): 5
        )

    """

    _T = TypeVar("_T", bound="Items")

    _repr_attrs: Tuple[str, ...] = ("type", "enum", "minimum", "maximum", "items")

    def __init__(
        self,
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

    @staticmethod
    def _convert_type(type_: _ArgType) -> Tuple[Union[str, List[str]], bool]:
        if isinstance(type_, Iterable) and not isinstance(type_, str):  # pylint: disable=W1116
            converted_types = [_AttributeType.get_type_name(single_type) for single_type in type_]
            return converted_types, "array" in converted_types

        converted_type = _AttributeType.get_type_name(type_)
        return converted_type, converted_type == "array"

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

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Load an Items from a dict containing the items information.

        Arguments:
            contents: A dict containing the information of the items.

        Returns:
            The loaded :class:`Items` object.

        Examples:
            >>> contents = {
            ...     "type": "array",
            ...     "enum": [1, 2, 3, 4, 5],
            ...     "minimum": 1,
            ...     "maximum": 5,
            ...     "items": {
            ...         "enum": [None],
            ...         "type": "null",
            ...     },
            ... }
            >>> Items.loads(contents)
            Items(
              (type): 'array',
              (enum): [...],
              (minimum): 1,
              (maximum): 5,
              (items): Items(...)
            )

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the information of the items into a dict.

        Returns:
            A dict containing all the information of the items.

        Examples:
            >>> items = Items(type_="integer", enum=[1, 2, 3, 4, 5], minimum=1, maximum=5)
            >>> items.dumps()
            {'type': 'integer', 'enum': [1, 2, 3, 4, 5], 'minimum': 1, 'maximum': 5}

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
    """This class represents the information of an attribute.

    It refers to the `Json schema`_ method to describe an attribute.

    .. todo::
        The format of argument *type_* on the generated web page is incorrect.

    Arguments:
        name: The name of the attribute.
        type_: The type of the attribute value, could be a single type or multi-types.
            The type must be within the followings:

                - array
                - boolean
                - integer
                - number
                - string
                - null
                - instance

        enum: All the possible values of an enumeration attribute.
        minimum: The minimum value of number type attribute.
        maximum: The maximum value of number type attribute.
        items: The items inside array type attributes.
        parent_categories: The parent categories of the attribute.
        description: The description of the attribute.

    Attributes:
        type: The type of the attribute value, could be a single type or multi-types.
        enum: All the possible values of an enumeration attribute.
        minimum: The minimum value of number type attribute.
        maximum: The maximum value of number type attribute.
        items: The items inside array type attributes.
        parent_categories: The parent categories of the attribute.
        description: The description of the attribute.

    .. _Json schema: https://json-schema.org/

    Examples:
        >>> from tensorbay.label import Items
        >>> items = Items(type_="integer", enum=[1, 2, 3, 4, 5], minimum=1, maximum=5)
        >>> AttributeInfo(
        ...     name="example",
        ...     type_="array",
        ...     enum=[1, 2, 3, 4, 5],
        ...     items=items,
        ...     minimum=1,
        ...     maximum=5,
        ...     parent_categories=["parent_category_of_example"],
        ...     description="This is an example",
        ... )
        AttributeInfo("example")(
          (type): 'array',
          (enum): [
            1,
            2,
            3,
            4,
            5
          ],
          (minimum): 1,
          (maximum): 5,
          (items): Items(
            (type): 'integer',
            (enum): [...],
            (minimum): 1,
            (maximum): 5
          ),
          (parent_categories): [
            'parent_category_of_example'
          ]
        )

    """

    _T = TypeVar("_T", bound="AttributeInfo")

    _repr_attrs = Items._repr_attrs + ("parent_categories",)
    _repr_maxlevel = 2

    _attrs_base: Items = attr_base(key=None)
    parent_categories: List[str] = attr(is_dynamic=True, key=camel)

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
        description: str = "",
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

        Arguments:
            contents: A dict containing the information of the attribute.

        Returns:
            The loaded :class:`AttributeInfo` object.

        Examples:
            >>> contents = {
            ...     "name": "example",
            ...     "type": "array",
            ...     "items": {"type": "boolean"},
            ...     "description": "This is an example",
            ...     "parentCategories": ["parent_category_of_example"],
            ... }
            >>> AttributeInfo.loads(contents)
            AttributeInfo("example")(
              (type): 'array',
              (items): Items(
                (type): 'boolean',
              ),
              (parent_categories): [
                'parent_category_of_example'
              ]
            )

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the information of this attribute into a dict.

        Returns:
            A dict containing all the information of this attribute.

        Examples:
            >>> from tensorbay.label import Items
            >>> items = Items(type_="integer", minimum=1, maximum=5)
            >>> attributeinfo = AttributeInfo(
            ...     name="example",
            ...     type_="array",
            ...     items=items,
            ...     parent_categories=["parent_category_of_example"],
            ...     description="This is an example",
            ... )
            >>> attributeinfo.dumps()
            {
                'name': 'example',
                'description': 'This is an example',
                'type': 'array',
                'items': {'type': 'integer', 'minimum': 1, 'maximum': 5},
                'parentCategories': ['parent_category_of_example'],
            }

        """
        return self._dumps()
