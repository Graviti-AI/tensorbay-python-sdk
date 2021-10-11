#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay import GAS
from tensorbay.client.gas import DEFAULT_BRANCH
from tensorbay.client.struct import ROOT_COMMIT_ID
from tensorbay.exception import ResourceNotExistError
from tests.utility import get_dataset_name


class TestCommit:
    def test_get_commit(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1", "commit-1-description")
        commit_1_id = dataset_client.status.commit_id
        dataset_client.create_draft("draft-2")
        dataset_client.commit("commit-2")
        commit_2_id = dataset_client.status.commit_id

        # Get top commit
        commit = dataset_client.get_commit(commit_2_id)
        assert commit.commit_id == commit_2_id
        assert commit.parent_commit_id == commit_1_id
        assert commit.title == "commit-2"
        assert commit.description == ""
        assert commit.committer.name
        assert commit.committer.date

        # Get one commit before the top one
        commit = dataset_client.get_commit(commit_1_id)
        assert commit.commit_id == commit_1_id
        assert commit.parent_commit_id == ROOT_COMMIT_ID
        assert commit.title == "commit-1"
        assert commit.description == "commit-1-description"
        assert commit.committer.name
        assert commit.committer.date

        gas_client.delete_dataset(dataset_name)

    def test_get_commit_by_revision(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1", "commit-1-description", tag="V1")
        commit_1_id = dataset_client.status.commit_id
        dataset_client.create_draft("draft-2")
        dataset_client.commit("commit-2")
        commit_2_id = dataset_client.status.commit_id

        # Get top commit by tag
        commit = dataset_client.get_commit("V1")
        assert commit.commit_id == commit_1_id
        assert commit.parent_commit_id == ROOT_COMMIT_ID
        assert commit.title == "commit-1"
        assert commit.description == "commit-1-description"
        assert commit.committer.name
        assert commit.committer.date

        # Get top commit by branch
        commit = dataset_client.get_commit(DEFAULT_BRANCH)
        assert commit.commit_id == commit_2_id
        assert commit.parent_commit_id == commit_1_id
        assert commit.title == "commit-2"
        assert commit.description == ""
        assert commit.committer.name
        assert commit.committer.date

        # The tag does not exists
        with pytest.raises(ResourceNotExistError):
            dataset_client.get_commit("V2")

        # Thr branch does not exists
        with pytest.raises(ResourceNotExistError):
            dataset_client.get_commit("main1")

        gas_client.delete_dataset(dataset_name)

    def test_list_commits(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1", tag="V1")
        commit_1_id = dataset_client.status.commit_id
        dataset_client.create_draft("draft-2")
        dataset_client.commit("commit-2")
        commit_2_id = dataset_client.status.commit_id
        dataset_client.create_draft("draft-3")
        dataset_client.commit("commit-3")
        commit_3_id = dataset_client.status.commit_id

        # List commits based on the top commit
        commits = dataset_client.list_commits(commit_3_id)
        assert len(commits) == 3
        assert commits[0].commit_id == commit_3_id
        assert commits[1].commit_id == commit_2_id
        assert commits[2].commit_id == commit_1_id

        # List commits based on one commit before the top one
        commits = dataset_client.list_commits(commit_2_id)
        assert len(commits) == 2
        assert commits[0].commit_id == commit_2_id
        assert commits[1].commit_id == commit_1_id

        # List commits based on tag
        commits = dataset_client.list_commits("V1")
        assert len(commits) == 1
        assert commits[0].commit_id == commit_1_id

        # List commits based on default branch
        commits = dataset_client.list_commits(DEFAULT_BRANCH)
        assert len(commits) == 3

        gas_client.delete_dataset(dataset_name)

    def test_list_commits_in_multi_branch_structure(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        commit_ids_main = []

        # Create 10 commits on the default branch
        for i in range(10):
            dataset_client.create_draft(f"draft-{i}")
            dataset_client.commit(f"commit-{i}", tag=f"main-V{i}")
            commit_ids_main.append(dataset_client.status.commit_id)

        # Create a branch "dev" on the 5th commit
        commit_ids_dev = commit_ids_main[0:5]
        dataset_client.create_branch("dev", commit_ids_main[4])

        # Create 10 commits on the branch "dev"
        for i in range(10):
            dataset_client.create_draft(f"draft-{i}")
            dataset_client.commit(f"commit-{i}", tag=f"dev-V{i}")
            commit_ids_dev.append(dataset_client.status.commit_id)

        # List commits based on the top commit in branch "dev"
        commits = dataset_client.list_commits(commit_ids_dev[-1])
        assert len(commits) == 15
        assert commits[0].commit_id == commit_ids_dev[-1]
        assert commits[-1].commit_id == commit_ids_dev[0]

        # List commits based on tag
        commits = dataset_client.list_commits("dev-V9")
        assert len(commits) == 15
        assert commits[0].commit_id == commit_ids_dev[-1]
        assert commits[-1].commit_id == commit_ids_dev[0]

        # List commits based on branch "dev"
        commits = dataset_client.list_commits("dev")
        assert len(commits) == 15
        assert commits[0].commit_id == commit_ids_dev[-1]
        assert commits[-1].commit_id == commit_ids_dev[0]

        # List commits based on default branch
        commits = dataset_client.list_commits(DEFAULT_BRANCH)
        assert len(commits) == 10
        assert commits[0].commit_id == commit_ids_main[-1]
        assert commits[-1].commit_id == commit_ids_main[0]

        gas_client.delete_dataset(dataset_name)
