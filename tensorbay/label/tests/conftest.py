#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# type: ignore

"""Pytest fixture config."""

import pytest

from ...utility import NameOrderedDict
from ..attributes import AttributeInfo
from ..supports import CategoryInfo

_DATA_CATEGORIES = {"categories": [{"name": "0"}, {"name": "1"}]}
_ENUMS = ["male", "female"]
_DATA_ATTRIBUTES = {"attributes": [{"name": "gender", "enum": _ENUMS}]}
_DATA_NAMES = [
    "L_shoulder",
    "L_Elbow",
    "L_wrist",
    "R_Shoulder",
    "R_Elbow",
]
_DATA_SKELETON = [(0, 1), (1, 2), (3, 4), (4, 5)]


@pytest.fixture
def categories():
    """Load CategoryInfo into a NameOrderedDict.

    Returns:
        A NameOrderedDict containing multiple CategoryInfo
    """
    category_dict = NameOrderedDict()
    for category in _DATA_CATEGORIES["categories"]:
        category_dict.append(CategoryInfo(category["name"]))
    return category_dict


@pytest.fixture
def attributes():
    """Load AttributeInfo into a NameOrderedDict.

    Returns:
        A NameOrderedDict containing multiple AttributeInfo
    """
    attribute_dict = NameOrderedDict()
    attribute_dict.append(AttributeInfo("gender", enum=_ENUMS))
    return attribute_dict
