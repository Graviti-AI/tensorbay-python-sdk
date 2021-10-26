#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
from textwrap import indent

import pytest

from tensorbay.cli.auth import INDENT
from tensorbay.cli.cli import draft
from tensorbay.cli.draft import _FULL_DRAFT_MESSAGE
from tensorbay.client.gas import DEFAULT_BRANCH
from tensorbay.client.struct import ROOT_COMMIT_ID


@pytest.mark.parametrize("is_fusion", [True, False])
def test_draft(
    mocker,
    invoke,
    is_fusion,
    mock_close_draft,
    mock_create_draft,
    mock_get_branch,
    mock_get_dataset,
    mock_list_drafts,
    mock_update_draft,
):
    dataset_name = "test_draft"
    tbrn = f"tb:{dataset_name}"
    wrong_tbrn = f"tb:{dataset_name}:test"
    draft_message = "Draft: {}\n" + _FULL_DRAFT_MESSAGE

    get_dataset, dataset_response = mock_get_dataset(mocker, is_fusion, False)
    dataset_id = dataset_response["id"]

    result = invoke(draft, [wrong_tbrn])
    assert result.exit_code == 1
    assert result.stderr == f'ERROR: To operate a draft, "{wrong_tbrn}" must be a dataset\n'
    get_dataset.assert_called_with(dataset_name)

    generate_branches, _ = mock_get_branch(mocker, dataset_id)
    revision_tbrn = f"tb:{dataset_name}@{DEFAULT_BRANCH}"
    result = invoke(draft, [revision_tbrn, "-l"])
    assert result.exit_code == 1
    assert (
        result.stderr
        == f'ERROR: list drafts based on given revision "{revision_tbrn}" is not supported\n'
    )
    generate_branches.assert_called_with(DEFAULT_BRANCH)

    list_drafts, draft_response = mock_list_drafts(mocker, DEFAULT_BRANCH)
    draft_tbrn = f"{tbrn}#1"
    draft1, draft2 = draft_response
    commit_id = f"({dataset_id})"
    description = f"{draft1.title}\n\n{indent(draft1.description, INDENT)}"
    draft1_output = draft_message.format(draft_tbrn, draft1.branch_name, commit_id, description)
    draft2_output = draft_message.format(f"{tbrn}#2", draft2.branch_name, commit_id, "<no title>")

    result = invoke(draft, [tbrn, "-l"])
    assert result.exit_code == 0
    assert result.stdout == f"{draft1_output}\n{draft2_output}\n"

    generate_branches, _ = mock_get_branch(mocker, ROOT_COMMIT_ID)
    result = invoke(draft, [draft_tbrn, "-l"])
    assert result.exit_code == 0
    assert (
        result.stdout
        == f'{draft_message.format(draft_tbrn, draft1.branch_name, "", description)}\n'
    )

    update_draft, _ = mock_update_draft(mocker)
    result = invoke(draft, [draft_tbrn, "-e", "-m", "draft1"])
    patch_data = {"title": "draft1", "description": ""}
    assert result.exit_code == 0
    assert (
        result.stdout == f'Successfully updated draft "{draft_tbrn}"\n'
        f'{_FULL_DRAFT_MESSAGE.format(draft1.branch_name, "", draft1.title)}\n'
    )
    update_draft.assert_called_with("PATCH", f"drafts/1", dataset_id, json=patch_data)

    list_drafts, _ = mock_list_drafts(mocker, "")
    result = invoke(draft, [draft_tbrn, "-l"])
    assert result.exit_code == 1
    assert result.stderr == "ERROR: Draft should be created based on a branch.\n"
    list_drafts.assert_called_with()

    result = invoke(draft, [draft_tbrn])
    assert result.exit_code == 1
    assert (
        result.stderr == f'ERROR: Create a draft in draft status "{draft_tbrn}" is not permitted\n'
    )

    result = invoke(draft, [tbrn, "-m", ""])
    assert result.exit_code == 1
    assert result.stderr == f"ERROR: Aborting creating draft due to empty draft message\n"

    create_draft, _ = mock_create_draft(mocker)
    result = invoke(draft, [tbrn, "-m", "draft1"])
    assert result.exit_code == 0
    assert (
        result.stdout == f'Successfully created draft "{draft_tbrn}"\n'
        f'{_FULL_DRAFT_MESSAGE.format(draft1.branch_name, "", draft1.title)}\n'
    )
    create_draft.assert_called_with(
        "POST", "drafts", dataset_id, json={"branchName": DEFAULT_BRANCH, "title": "draft1"}
    )

    result = invoke(draft, [tbrn, "-e"])
    assert result.exit_code == 1
    assert result.stderr == "ERROR: Draft number is required when editing draft\n"

    result = invoke(draft, [draft_tbrn, "-e", "-m", ""])
    assert result.exit_code == 1
    assert result.stderr == "ERROR: Aborting updating draft due to empty draft message\n"

    result = invoke(draft, [tbrn, "-c"])
    assert result.exit_code == 1
    assert result.stderr == "ERROR: Draft number is required when editing draft\n"

    delete_draft, delete_response = mock_close_draft(mocker)
    result = invoke(draft, [draft_tbrn, "-c"])
    assert result.exit_code == 0
    assert result.stdout == f'Successfully closed draft "{draft_tbrn}"\n'
    delete_draft.assert_called_with("PATCH", f"drafts/1", dataset_id, json=delete_response)
