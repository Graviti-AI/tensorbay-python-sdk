#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from tensorbay.client import gas
from tensorbay.client.dataset import DatasetClient
from tensorbay.client.gas import DEFAULT_BRANCH, DEFAULT_IS_PUBLIC, GAS
from tensorbay.client.status import Status
from tensorbay.client.struct import ROOT_COMMIT_ID
from tensorbay.client.tests.utility import mock_response


class TestVersionControlClient:
    gas_client = GAS("Accesskey-********************************")
    dataset_client = DatasetClient(
        "test_dataset",
        "12345",
        gas_client,
        status=Status(DEFAULT_BRANCH, commit_id=ROOT_COMMIT_ID),
        alias="",
        is_public=DEFAULT_IS_PUBLIC,
    )

    def test_squash_and_merge(self, mocker):
        post_data = {
            "title": "squash_merge-1",
            "sourceBranchName": "branch-1",
            "targetBranchName": "branch-2",
            "strategy": "abort",
        }
        response_data = {"draftNumber": 2}
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=response_data),
        )
        draft_number = self.dataset_client.squash_and_merge(
            "squash_merge-1",
            source_branch_name="branch-1",
            target_branch_name="branch-2",
            strategy="abort",
        )
        open_api_do.assert_called_once_with(
            "POST", "squashAndMerge", self.dataset_client.dataset_id, json=post_data
        )
        assert draft_number == 2
