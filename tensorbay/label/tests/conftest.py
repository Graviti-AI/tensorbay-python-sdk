#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# type: ignore
# pylint: disable=redefined-outer-name

"""Pytest fixture config."""

import pytest

from tensorbay.label.attributes import AttributeInfo
from tensorbay.label.supports import CategoryInfo, KeypointsInfo
from tensorbay.utility import NameList


@pytest.fixture
def attributes_catalog_data():
    """Argument for attributes in catalog.

    Returns:
        A list containing attributes info.
    """
    return [
        {"name": "gender", "enum": ["male", "female"]},
        {"name": "occluded", "type": "integer", "minimum": 1, "maximum": 5},
    ]


@pytest.fixture
def categories_catalog_data():
    """Argument for categories in catalog.

    Returns:
        A list containing categories info.
    """
    return [
        {
            "name": "0",
            "description": "This is an exmaple of test",
        },
        {
            "name": "1",
            "description": "This is an exmaple of test",
        },
    ]


@pytest.fixture
def mask_categories_catalog_data():
    """Argument for mask categories in catalog.

    Returns:
        A list containing mask categories info.
    """
    return [
        {"name": "cat", "description": "This is an exmaple of test", "categoryId": 0},
        {"name": "dog", "description": "This is an exmaple of test", "categoryId": 10},
    ]


@pytest.fixture(params=[True, False])
def is_tracking_data(request):
    """Argument for is_tracking.

    Arguments:
        request: A request for a fixture from a fixture function.

    Returns:
        True or False.
    """
    return request.param


@pytest.fixture
def keypoints_info_data():
    """Argument for KeypointsInfo.

    Returns:
        A dict containing keypoints info.
    """
    return {
        "number": 5,
        "names": [
            "L_shoulder",
            "L_Elbow",
            "L_wrist",
            "R_Shoulder",
            "R_Elbow",
        ],
        "skeleton": [(0, 1), (1, 2), (3, 4), (4, 5)],
        "visible": "TERNARY",
        "parentCategories": ["person"],
        "description": "test description",
    }


@pytest.fixture
def categories(categories_catalog_data):
    """Load CategoryInfo into a NameList.

    Arguments:
        categories_catalog_data: A list containing categories info.

    Returns:
        A NameList containing multiple CategoryInfo.
    """
    category_dict = NameList()
    for category in categories_catalog_data:
        category_dict.append(CategoryInfo.loads(category))
    return category_dict


@pytest.fixture
def attributes(attributes_catalog_data):
    """Load AttributeInfo into a NameList.

    Arguments:
        attributes_catalog_data: A list containing attributes info.

    Returns:
        A NameList containing multiple AttributeInfo.
    """
    attribute_dict = NameList()
    for attribute in attributes_catalog_data:
        attribute_dict.append(AttributeInfo.loads(attribute))
    return attribute_dict


@pytest.fixture
def keypoints(keypoints_info_data):
    """Load keypoints info data into KeypointsInfo.

    Arguments:
        keypoints_info_data: A dict containing keypoints info.

    Returns:
        A loaded KeypointsInfo.
    """
    return KeypointsInfo.loads(keypoints_info_data)
