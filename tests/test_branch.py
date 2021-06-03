#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay import GAS
from tensorbay.client.gas import DEFAULT_BRANCH
from tensorbay.exception import OperationError, ResourceNotExistError, ResponseSystemError

from .utility import get_dataset_name


class TestBranch:
    def test_create_branch(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)

        # Creating the branch in a empty repo is not allowed
        with pytest.raises(ResponseSystemError):
            dataset_client.create_branch("T123")

        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1", tag="V1")
        dataset_client.create_branch("T123")
        branch = dataset_client.get_branch("T123")

        assert branch.name == "T123"
        assert branch.commit_id == dataset_client.status.commit_id
        assert branch.parent_commit_id is None
        assert branch.message == "commit-1"
        assert branch.committer.name
        assert branch.committer.date

        gas_client.delete_dataset(dataset_name)

    def test_create_branch_on_revision(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)

        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1", tag="V1")
        commit_id = dataset_client.status.commit_id
        dataset_client.create_draft("draft-2")
        dataset_client.commit("commit-2", tag="V2")

        dataset_client.create_branch("Test_Commit_Id", revision=commit_id)
        dataset_client.create_branch("Test_Tag", revision="V1")
        dataset_client.create_branch("Test_Branch", revision="main")

        branch = dataset_client.get_branch("Test_Commit_Id")
        assert branch.name == "Test_Commit_Id"
        assert branch.commit_id == commit_id
        assert branch.parent_commit_id is None
        assert branch.message == "commit-1"

        branch = dataset_client.get_branch("Test_Tag")
        assert branch.name == "Test_Tag"
        assert branch.commit_id == commit_id
        assert branch.parent_commit_id is None
        assert branch.message == "commit-1"

        branch = dataset_client.get_branch("Test_Branch")
        assert branch.name == "Test_Branch"
        assert branch.commit_id == dataset_client.status.commit_id
        assert branch.parent_commit_id == commit_id
        assert branch.message == "commit-2"

        gas_client.delete_dataset(dataset_name)

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

        dataset_client.create_branch("T123")

        branch = dataset_client.get_branch("main")
        assert branch.name == "main"
        assert branch.commit_id == commit_2_id
        assert branch.parent_commit_id == commit_1_id
        assert branch.message == "commit-2"
        assert branch.committer.name
        assert branch.committer.date
        with pytest.raises(ResourceNotExistError):
            dataset_client.get_branch("main1")

        branch1 = dataset_client.get_branch("T123")
        assert branch1.name == "T123"
        assert branch1.commit_id == commit_2_id
        assert branch1.parent_commit_id == commit_1_id
        assert branch1.message == "commit-2"
        assert branch1.committer.name
        assert branch1.committer.date

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

    def test_delete_branch(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1")
        dataset_client.create_branch("T123")

        # Deleting the current branch is not allowed
        with pytest.raises(OperationError):
            dataset_client.delete_branch("T123")

        dataset_client.checkout(revision=DEFAULT_BRANCH)
        dataset_client.delete_branch("T123")

        with pytest.raises(ResourceNotExistError):
            dataset_client.get_branch("T123")
