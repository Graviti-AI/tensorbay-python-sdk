#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# type: ignore
# pylint: disable=redefined-outer-name

"""Pytest fixture config."""

import pytest

from ...utility import NameOrderedDict
from ..attributes import AttributeInfo
from ..supports import CategoryInfo


@pytest.fixture
def attributes_catalog_data():
    """Argument for attributes in catalog.

    Returns:
        A list containing attributes info
    """
    return [{"name": "gender", "enum": ["male", "female"]}]


@pytest.fixture
def categories_catalog_data():
    """Argument for categories in catalog.

    Returns:
        A list containing categories info
    """
    return [{"name": "0"}, {"name": "1"}]


@pytest.fixture(params=[True, False])
def is_tracking_data(request):
    """Argument for is_tracking.

    Arguments:
        request: A request for a fixture from a fixture function.

    Returns:
        True or False
    """
    return request.param


@pytest.fixture
def categories(categories_catalog_data):
    """Load CategoryInfo into a NameOrderedDict.

    Arguments:
        categories_catalog_data: A list containing categories info.

    Returns:
        A NameOrderedDict containing multiple CategoryInfo
    """
    category_dict = NameOrderedDict()
    for category in categories_catalog_data:
        category_dict.append(CategoryInfo.loads(category))
    return category_dict


@pytest.fixture
def attributes(attributes_catalog_data):
    """Load AttributeInfo into a NameOrderedDict.

    Arguments:
        attributes_catalog_data: A list containing attributes info.

    Returns:
        A NameOrderedDict containing multiple AttributeInfo
    """
    attribute_dict = NameOrderedDict()
    for attribute in attributes_catalog_data:
        attribute_dict.append(AttributeInfo.loads(attribute))
    return attribute_dict
