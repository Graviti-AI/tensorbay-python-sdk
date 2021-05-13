#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay import GAS
from tensorbay.exception import ResourceNotExistError

from .utility import get_dataset_name


class TestBranch:
    def test_get_branch(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1", tag="V1")
        commit_1_id = dataset_client.status.commit_id
        dataset_client.create_draft("draft-2")
        dataset_client.commit("commit-2")
        commit_2_id = dataset_client.status.commit_id

        branch = dataset_client.get_branch("main")
        assert branch.name == "main"
        assert branch.commit_id == commit_2_id
        assert branch.parent_commit_id == commit_1_id
        assert branch.message == "commit-2"
        assert branch.committer.name
        assert branch.committer.date
        with pytest.raises(ResourceNotExistError):
            dataset_client.get_branch("main1")

        gas_client.delete_dataset(dataset_name)

    def test_list_branches(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1", tag="V1")

        commit_1_id = dataset_client.status.commit_id

        branches = dataset_client.list_branches()
        assert len(branches) == 1
        assert branches[0].name == "main"
        assert branches[0].commit_id == commit_1_id

        gas_client.delete_dataset(dataset_name)
