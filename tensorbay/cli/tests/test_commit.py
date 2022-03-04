#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
import pytest

from tensorbay.cli.cli import commit
from tensorbay.cli.tests.conftest import assert_cli_fail, assert_cli_success
from tensorbay.client.gas import DEFAULT_BRANCH


@pytest.mark.parametrize("is_fusion", [True, False])
def test_commit(
    mocker,
    invoke,
    is_fusion,
    mock_list_drafts,
    mock_create_commit,
    mock_get_dataset,
):

    dataset_name = "test_commit"
    tbrn = f"tb:{dataset_name}"
    wrong_tbrn = f"tb:{dataset_name}:test"
    draft_tbrn = f"{tbrn}#1"
    commit_tbrn = f"{tbrn}@1"

    get_dataset, dataset_response = mock_get_dataset(mocker, is_fusion, False)
    dataset_id = dataset_response["id"]

    result = invoke(commit, [wrong_tbrn])
    assert_cli_fail(result, f'ERROR: To operate a commit, "{wrong_tbrn}" must be a dataset\n')
    get_dataset.assert_called_with(dataset_name)

    result = invoke(commit, [tbrn])
    assert_cli_fail(
        result, f'ERROR: To commit, "{tbrn}" must be in draft status, like "{draft_tbrn}"\n'
    )

    create_draft, _ = mock_list_drafts(mocker, DEFAULT_BRANCH)
    result = invoke(commit, [draft_tbrn, "-m", ""])
    assert_cli_fail(result, "ERROR: Aborting commit due to empty commit message\n")
    create_draft.assert_called_with()

    create_commit, commit_response = mock_create_commit(mocker)
    draftNumber = commit_response["commitId"]
    result = invoke(commit, [draft_tbrn, "-m", "commit1"])
    assert_cli_success(result, f"Committed successfully: {draft_tbrn} -> {commit_tbrn}\n")
    create_commit.assert_called_with(
        "POST", "commits", dataset_id, json={"draftNumber": draftNumber, "title": "commit1"}
    )
