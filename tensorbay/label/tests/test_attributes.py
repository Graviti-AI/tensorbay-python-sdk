#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from .. import AttributeInfo, Items
from ..attributes import _AttributeType

_ATTRIBUTETYPE_NAME = ["array", "boolean", "integer", "number", "string", "null", "instance"]
_ENUM = [1, 2, 3, 4, 5]
_MINIMUM = 1
_MAXIMUM = 5
_DESCRIPTION = "This is an example of test"
_PARENTCATEGORIES = ["parent_category_of_test"]

_ITEMS_DATA = {
    "type": "array",
    "enum": _ENUM,
    "minimum": _MINIMUM,
    "maximum": _MAXIMUM,
    "items": {
        "enum": [None],
        "type": "null",
    },
}

_ATTRIBUTEINFO_DATA = {
    "name": "test",
    "type": "array",
    "enum": _ENUM,
    "items": {
        "enum": ["true", "false"],
        "type": "boolean",
    },
    "minimum": _MINIMUM,
    "maximum": _MAXIMUM,
    "description": _DESCRIPTION,
    "parentCategories": _PARENTCATEGORIES,
}


class TestAttributeType:
    def test_get_type_name(self):
        with pytest.raises(ValueError):
            _AttributeType.get_type_name("bool")

        for name in _ATTRIBUTETYPE_NAME:
            assert _AttributeType.get_type_name(name) == name


class TestItems:
    def test_init(self):
        item = Items(type_="integer", enum=_ENUM, minimum=1, maximum=5)

        assert item.type == "integer"
        assert item.enum == _ENUM
        assert item.minimum == _MINIMUM
        assert item.maximum == _MAXIMUM

    def test_eq(self):
        item_1 = Items(type_="integer", enum=_ENUM, minimum=1, maximum=5)
        item_2 = Items(type_="integer", enum=_ENUM, minimum=1, maximum=5)
        item_3 = Items(type_="number", enum=_ENUM, minimum=1, maximum=5)
        assert item_1 == item_2
        assert item_1 != item_3

    def test_convert_type(self):
        converted_type_1 = Items(enum=_ENUM)._convert_type("array")
        assert converted_type_1 == ("array", True)

        converted_type_2 = Items(enum=_ENUM)._convert_type("integer")
        assert converted_type_2 == ("integer", False)

    def test_loads(self):
        items = Items.loads(_ITEMS_DATA)

        assert items.type == _ITEMS_DATA["type"]
        assert items.enum == _ITEMS_DATA["enum"]
        assert items.minimum == _ITEMS_DATA["minimum"]
        assert items.maximum == _ITEMS_DATA["maximum"]
        assert items.items.type == _ITEMS_DATA["items"]["type"]
        assert items.items.enum == _ITEMS_DATA["items"]["enum"]

    def test_dumps(self):
        items_type = _ITEMS_DATA["items"]["type"]
        items_enum = _ITEMS_DATA["items"]["enum"]
        items = Items(type_=items_type, enum=items_enum)
        type = _ITEMS_DATA["type"]

        item = Items(type_=type, enum=_ENUM, minimum=_MINIMUM, maximum=_MAXIMUM, items=items)
        assert item.dumps() == _ITEMS_DATA


class TestAttributeInfo:
    def test_init(self):
        name = "test"
        enum_items = [1, 2, 3]
        items = Items(type_="integer", enum=enum_items, minimum=1, maximum=5)

        attributeinfo = AttributeInfo(
            name=name,
            type_="array",
            enum=_ENUM,
            items=items,
            minimum=_MINIMUM,
            maximum=_MAXIMUM,
            parent_categories=_PARENTCATEGORIES,
            description=_DESCRIPTION,
        )

        assert attributeinfo.name == name
        assert attributeinfo.type == "array"
        assert attributeinfo.enum == _ENUM
        assert attributeinfo.items == items
        assert attributeinfo.minimum == _MINIMUM
        assert attributeinfo.maximum == _MAXIMUM
        assert attributeinfo.parent_categories == _PARENTCATEGORIES
        assert attributeinfo.description == _DESCRIPTION

    def test_eq(self):
        attributeinfo_v1 = AttributeInfo(
            name="traffic_light_color",
            type_=["array", "null"],
            items=Items(
                type_="integer",
                enum=_ENUM,
                minimum=_MINIMUM,
                maximum=_MAXIMUM,
            ),
            parent_categories=["a", "b"],
            description=_DESCRIPTION,
        )
        attributeinfo_v2 = AttributeInfo(
            name="traffic_light_color",
            type_=["array", "null"],
            items=Items(
                type_="integer",
                enum=_ENUM,
                minimum=_MINIMUM,
                maximum=_MAXIMUM,
            ),
            parent_categories=["a", "b"],
            description=_DESCRIPTION,
        )
        attributeinfo_v3 = AttributeInfo(
            name="traffic_light_color",
            type_=["array", "null"],
            items=Items(
                type_="integer",
                enum=_ENUM,
                minimum=_MINIMUM,
                maximum=_MAXIMUM,
            ),
            parent_categories=["b", "a"],
            description=_DESCRIPTION,
        )

        assert attributeinfo_v1 == attributeinfo_v2
        assert attributeinfo_v1 != attributeinfo_v3

    def test_loads(self):
        attributeinfo = AttributeInfo.loads(_ATTRIBUTEINFO_DATA)

        assert attributeinfo.name == _ATTRIBUTEINFO_DATA["name"]
        assert attributeinfo.type == _ATTRIBUTEINFO_DATA["type"]
        assert attributeinfo.enum == _ATTRIBUTEINFO_DATA["enum"]
        assert attributeinfo.minimum == _ATTRIBUTEINFO_DATA["minimum"]
        assert attributeinfo.maximum == _ATTRIBUTEINFO_DATA["maximum"]
        assert attributeinfo.items.enum == _ATTRIBUTEINFO_DATA["items"]["enum"]
        assert attributeinfo.items.type == _ATTRIBUTEINFO_DATA["items"]["type"]
        assert attributeinfo.description == _ATTRIBUTEINFO_DATA["description"]
        assert attributeinfo.parent_categories == _ATTRIBUTEINFO_DATA["parentCategories"]

    def test_dumps(self):
        name = _ATTRIBUTEINFO_DATA["name"]
        items_enum = _ATTRIBUTEINFO_DATA["items"]["enum"]
        items_type = _ATTRIBUTEINFO_DATA["items"]["type"]
        items = Items(type_=items_type, enum=items_enum)

        attributeinfo = AttributeInfo(
            name=name,
            type_="array",
            enum=_ENUM,
            items=items,
            minimum=_MINIMUM,
            maximum=_MAXIMUM,
            parent_categories=_PARENTCATEGORIES,
            description=_DESCRIPTION,
        )

        attributeinfo.dumps() == _ATTRIBUTEINFO_DATA
