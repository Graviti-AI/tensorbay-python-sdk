#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# type: ignore
# pylint: disable=redefined-outer-name

"""Pytest fixture config."""

import pytest

from ..attributes import AttributesInfo
from ..supports import CategoriesInfo, KeypointsInfo


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
    """Load CategoryInfo into a CategoriesInfo.

    Arguments:
        categories_catalog_data: A list containing categories info.

    Returns:
        A CategoriesInfo containing multiple CategoryInfo.
    """
    return CategoriesInfo.loads(categories_catalog_data)


@pytest.fixture
def attributes(attributes_catalog_data):
    """Load the attributes_catalog_data into a AttributesInfo.

    Arguments:
        attributes_catalog_data: A list containing attributes info.

    Returns:
        A AttributesInfo containing multiple AttributeInfo.
    """
    return AttributesInfo.loads(attributes_catalog_data)


@pytest.fixture
def keypoints(keypoints_info_data):
    """Load keypoints info data into KeypointsInfo.

    Arguments:
        keypoints_info_data: A dict containing keypoints info.

    Returns:
        A loaded KeypointsInfo.
    """
    return KeypointsInfo.loads(keypoints_info_data)
