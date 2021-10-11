#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay.label import AttributeInfo, Items
from tensorbay.label.attributes import _AttributeType


class TestAttributeType:
    def test_get_type_name(self):
        with pytest.raises(ValueError):
            _AttributeType.get_type_name("bool")

        for name in ("array", "boolean", "integer", "number", "string", "null", "instance"):
            assert _AttributeType.get_type_name(name) == name


class TestItems:
    def test_init(self):
        item = Items(type_="integer", enum=[1, 2], minimum=1, maximum=5)

        assert item.type == "integer"
        assert item.enum == [1, 2]
        assert item.minimum == 1
        assert item.maximum == 5

    def test_eq(self):
        item_1 = Items(type_="integer", enum=[1, 2], minimum=1, maximum=5)
        item_2 = Items(type_="integer", enum=[1, 2], minimum=1, maximum=5)
        item_3 = Items(type_="number", enum=[1, 2], minimum=1, maximum=5)
        assert item_1 == item_2
        assert item_1 != item_3

    def test_convert_type(self):
        converted_type_1 = Items(enum=[1, 2])._convert_type("array")
        assert converted_type_1 == ("array", True)

        converted_type_2 = Items(enum=[1, 2])._convert_type("integer")
        assert converted_type_2 == ("integer", False)

    def test_loads(self):
        content = {
            "type": "array",
            "enum": [1, 2],
            "minimum": 1,
            "maximum": 5,
            "items": {
                "enum": [None],
                "type": "null",
            },
        }
        items = Items.loads(content)

        assert items.type == "array"
        assert items.enum == [1, 2]
        assert items.minimum == 1
        assert items.maximum == 5
        assert items.items.type == "null"
        assert items.items.enum == [None]

    def test_dumps(self):
        items = Items(type_="null", enum=[None])
        item = Items(type_="array", enum=[1, 2], minimum=1, maximum=5, items=items)
        assert item.dumps() == {
            "type": "array",
            "enum": [1, 2],
            "minimum": 1,
            "maximum": 5,
            "items": {
                "enum": [None],
                "type": "null",
            },
        }


class TestAttributeInfo:
    def test_init(self):
        name = "test"
        enum_items = [1, 2, 3]
        items = Items(type_="integer", enum=enum_items, minimum=1, maximum=5)

        attributeinfo = AttributeInfo(
            name=name,
            type_="array",
            enum=[1, 2],
            items=items,
            minimum=1,
            maximum=5,
            parent_categories=["parent"],
            description="Hello",
        )

        assert attributeinfo.name == name
        assert attributeinfo.type == "array"
        assert attributeinfo.enum == [1, 2]
        assert attributeinfo.items == items
        assert attributeinfo.minimum == 1
        assert attributeinfo.maximum == 5
        assert attributeinfo.parent_categories == ["parent"]
        assert attributeinfo.description == "Hello"

    def test_eq(self):
        attributeinfo_v1 = AttributeInfo(
            name="traffic_light_color",
            type_=["array", "null"],
            items=Items(
                type_="integer",
                enum=[1, 2],
                minimum=1,
                maximum=5,
            ),
            parent_categories=["a", "b"],
            description="Hello",
        )
        attributeinfo_v2 = AttributeInfo(
            name="traffic_light_color",
            type_=["array", "null"],
            items=Items(
                type_="integer",
                enum=[1, 2],
                minimum=1,
                maximum=5,
            ),
            parent_categories=["a", "b"],
            description="Hello",
        )
        attributeinfo_v3 = AttributeInfo(
            name="traffic_light_color",
            type_=["array", "null"],
            items=Items(
                type_="integer",
                enum=[1, 2],
                minimum=1,
                maximum=5,
            ),
            parent_categories=["b", "a"],
            description="Hello",
        )

        assert attributeinfo_v1 == attributeinfo_v2
        assert attributeinfo_v1 != attributeinfo_v3

    def test_loads(self):
        content = {
            "name": "test",
            "type": "array",
            "enum": [1, 2],
            "items": {
                "enum": ["true", "false"],
                "type": "boolean",
            },
            "minimum": 1,
            "maximum": 5,
            "description": "Hello",
            "parentCategories": ["parent"],
        }
        attributeinfo = AttributeInfo.loads(content)

        assert attributeinfo.name == "test"
        assert attributeinfo.type == "array"
        assert attributeinfo.enum == [1, 2]
        assert attributeinfo.minimum == 1
        assert attributeinfo.maximum == 5
        assert attributeinfo.items.enum == ["true", "false"]
        assert attributeinfo.items.type == "boolean"
        assert attributeinfo.description == "Hello"
        assert attributeinfo.parent_categories == ["parent"]

    def test_dumps(self):
        items = Items(type_="boolean", enum=["true", "false"])

        attributeinfo = AttributeInfo(
            name="test",
            type_="array",
            enum=[1, 2],
            items=items,
            minimum=1,
            maximum=5,
            parent_categories=["parent"],
            description="Hello",
        )

        attributeinfo.dumps() == {
            "name": "test",
            "type": "array",
            "enum": [1, 2],
            "items": {
                "enum": ["true", "false"],
                "type": "boolean",
            },
            "minimum": 1,
            "maximum": 5,
            "description": "Hello",
            "parentCategories": ["parent"],
        }
