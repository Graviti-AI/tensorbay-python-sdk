#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# type: ignore
# pylint: disable=redefined-outer-name

"""The implementation of the pytest fixture function."""

import sys

import pytest

from tensorbay.client import gas, segment, version
from tensorbay.client.gas import DEFAULT_BRANCH
from tensorbay.client.struct import Branch, Draft
from tensorbay.client.tests.utility import mock_response
from tensorbay.dataset import RemoteData
from tensorbay.exception import UnauthorizedError


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
        The patched mocker and response data.

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
        The patched mocker and response data.

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
        The patched mocker and response data.

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
        The patched mocker and response data.

    """
    response_data = [f"data{i}.png" for i in range(2)]
    return (
        mocker.patch(
            f"{segment.__name__}.SegmentClient.list_data_paths",
            return_value=response_data,
        ),
        response_data,
    )


@function_fixture
def mock_get_data(mocker, remote_path):
    """Mock the get_data funcion of SegmentClient class.

    Arguments:
        mocker: The mocker fixture.
        remote_path: The remote path of data.

    Returns:
        The patched mocker and response data.

    """
    response_data = [RemoteData(remote_path=remote_path)]
    return (
        mocker.patch(
            f"{segment.__name__}.SegmentClient.get_data",
            return_value=response_data,
        ),
        response_data,
    )


@function_fixture
def mock_create_dataset(mocker):
    """Mock the createDataset OpenAPI.

    Arguments:
        mocker: The mocker fixture.

    Returns:
        The patched mocker and response data.

    """
    response_data = {"id": "123456"}
    return (
        mocker.patch(
            f"{gas.__name__}.Client.open_api_do", return_value=mock_response(data=response_data)
        ),
        response_data,
    )


@function_fixture
def mock_delete_dataset(mocker, is_fusion, is_public, mock_get_dataset):
    """Mock the deleteDataset OpenAPI.

    Arguments:
        mocker: The mocker fixture.
        is_fusion: Whether the dataset is a fusion dataset.
        is_public: Whether the dataset is a public dataset.
        mock_get_dataset: Mock the _get_dataset method of GAS class.

    Returns:
        The patched mocker and response data.

    """
    _, response_data = mock_get_dataset(mocker, is_fusion, is_public)
    return (
        mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=response_data,
        ),
        response_data,
    )


@function_fixture
def mock_list_drafts(mocker, branch_name):
    """Mock the list_drafts method of VersionControlMixin class.

    Arguments:
        mocker: The mocker fixture.
        branch_name: The branch name of draft.

    Returns:
        The patched mocker and response data.

    """
    drafts = [
        {
            "number": 1,
            "title": "draft1",
            "branchName": branch_name,
            "status": "OPEN",
            "parentCommitId": "4c564ea07f4e47679ec8c63d238bb3a1",
            "author": {"name": "draft author", "date": 1636967807},
            "updatedAt": 1636967807,
            "description": "first draft of test_draft",
        },
        {
            "number": 2,
            "title": "",
            "branchName": branch_name,
            "status": "CLOSED",
            "parentCommitId": "4c564ea07f4e47679ec8c63d238bb3a1",
            "author": {"name": "draft author", "date": 1636967807},
            "updatedAt": 1636967807,
            "description": "",
        },
    ]
    response = [Draft.loads(draft_response) for draft_response in drafts]
    return (
        mocker.patch(f"{version.__name__}.VersionControlMixin.list_drafts", return_value=response),
        response,
    )


@function_fixture
def mock_get_branch(mocker, commit_id):
    """Mock the get_branch method of VersionControlMixin class.

    Arguments:
        mocker: The mocker fixture.
        commit_id: The commit id of the branch.

    Returns:
        The patched mocker and response data.

    """
    response_data = Branch.loads(
        {
            "name": DEFAULT_BRANCH,
            "commitId": commit_id,
            "parentCommitId": "",
            "title": "test_draft",
            "description": "",
            "committer": {"name": "", "date": 1632454975},
        }
    )
    return (
        mocker.patch(
            f"{version.__name__}.VersionControlMixin.get_branch", return_value=response_data
        ),
        response_data,
    )


@function_fixture
def mock_update_draft(mocker):
    """Mock the updateDraft OpenAPI.

    Arguments:
        mocker: The mocker fixture.

    Returns:
        The patched mocker and response data.

    """
    response_data = {"draftNumber": 1}
    return (
        mocker.patch(
            f"{gas.__name__}.Client.open_api_do", return_value=mock_response(data=response_data)
        ),
        response_data,
    )


@function_fixture
def mock_create_draft(mocker):
    """Mock the createDraft OpenAPI.

    Arguments:
        mocker: The mocker fixture.

    Returns:
        The patched mocker and response data.

    """
    response_data = {"draftNumber": 1}
    return (
        mocker.patch(
            f"{gas.__name__}.Client.open_api_do", return_value=mock_response(data=response_data)
        ),
        response_data,
    )


@function_fixture
def mock_close_draft(mocker):
    """Mock the closeDraft OpenAPI.

    Arguments:
        mocker: The mocker fixture.

    Returns:
        The patched mocker and response data.

    """
    response_data = {"status": "CLOSED"}
    return (
        mocker.patch(
            f"{gas.__name__}.Client.open_api_do", return_value=mock_response(data=response_data)
        ),
        response_data,
    )


@function_fixture
def mock_list_data_details(mocker, num: int = 1):
    """Mock the getDataDetails openAPI.

    Arguments:
        mocker: The mocker fixture.
        num: The number of data.

    Returns:
        The patched mocker and response data.

    """
    response_data = {
        "dataDetails": [
            {
                "remotePath": f"data{i}.png",
                "timestamp": 1614667532,
                "label": {},
                "url": "url",
            }
            for i in range(num)
        ],
        "offset": 0,
        "recordSize": num,
        "totalCount": num,
    }
    return (
        mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=response_data),
        ),
        response_data,
    )


@function_fixture
def mock_get_total_size(mocker, large: bool = False):
    """Mock the getTotalSize openAPI.

    Arguments:
        mocker: The mocker fixture.
        large: Whether the dataset size is large than free storage.

    Returns:
        The patched mocker and response data.

    """
    response_data = {"totalSize": 7 if not large else sys.maxsize}
    return (
        mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=response_data),
        ),
        response_data,
    )


@function_fixture
def mock_get_users(mocker, is_valid):
    """Mock the getUsers OpenAPI.

    Arguments:
        mocker: The mocker fixture.
        is_valid: Whether the mock need raise UnauthorizedError.

    Returns:
        The patched mocker and response data.

    """
    response_data = {
        "id": "3713a28*************************",
        "nickname": "test",
        "email": "test***@graviti.cn",
        "mobile": "180********",
        "description": "",
        "team": {
            "id": "7d3e****************************",
            "name": "Test",
            "email": None,
            "description": "",
        },
    }
    mock = mocker.patch(
        f"{gas.__name__}.Client.open_api_do", return_value=mock_response(data=response_data)
    )
    if is_valid is False:
        mock.side_effect = UnauthorizedError()

    return mock, response_data
