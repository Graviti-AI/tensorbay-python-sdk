#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# type: ignore
# pylint: disable=redefined-outer-name

"""Pytest fixture config."""

import pytest

from tensorbay.client import gas, segment
from tensorbay.client.gas import DEFAULT_BRANCH
from tensorbay.client.tests.utility import mock_response


def function_fixture(fixture):
    """A decorator that makes fixture only run when it is called.

    Arguments:
        fixture: The fixture.

    Returns:
        The wrapped fixture.

    """

    @pytest.fixture
    def wrapper():
        return fixture

    return wrapper


@function_fixture
def mock_list_datasets(mocker):
    """Mock the listDatasets OpenAPI.

    Arguments:
        mocker: The mocker fixture.

    Returns:
        The pached mocker and response data.

    """
    response_data = {
        "datasets": [
            {
                "id": "123456",
                "name": "test",
                "type": 0,
                "defaultBranch": DEFAULT_BRANCH,
                "updateTime": 1622530298,
                "owner": "",
            }
        ],
        "offset": 0,
        "recordSize": 1,
        "totalCount": 1,
    }
    return (
        mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=response_data),
        ),
        response_data,
    )


@function_fixture
def mock_get_dataset(mocker, is_fusion, is_public):
    """Mock the _get_dataset funcion of GAS class.

    Arguments:
        mocker: The mocker fixture.
        is_fusion: Whether the dataset is a fusion dataset.
        is_public: Whether the dataset is a public dataset.

    Returns:
        The pached mocker and response data.

    """
    response_data = {
        "id": "123456",
        "type": int(is_fusion),
        "commitId": "4",
        "defaultBranch": DEFAULT_BRANCH,
        "alias": "alias",
        "isPublic": is_public,
    }
    return (
        mocker.patch(
            f"{gas.__name__}.GAS._get_dataset",
            return_value=response_data,
        ),
        response_data,
    )


@function_fixture
def mock_list_segments(mocker):
    """Mock the listSegments OpenAPI.

    Arguments:
        mocker: The mocker fixture.

    Returns:
        The pached mocker and response data.

    """
    response_data = {
        "offset": 0,
        "recordSize": 2,
        "totalCount": 2,
        "segments": [
            {"name": "segment0", "description": ""},
            {"name": "segment1", "description": ""},
        ],
    }
    return (
        mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=response_data),
        ),
        response_data,
    )


@function_fixture
def mock_paths(mocker):
    """Mock the list_data_paths funcion of SegmentClient class.

    Arguments:
        mocker: The mocker fixture.

    Returns:
        The pached mocker and response data.

    """
    response_data = [f"data{i}.png" for i in range(2)]
    return (
        mocker.patch(
            f"{segment.__name__}.SegmentClient.list_data_paths",
            return_value=response_data,
        ),
        response_data,
    )
