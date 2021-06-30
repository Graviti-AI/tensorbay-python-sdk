#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay import GAS
from tensorbay.client.gas import DEFAULT_BRANCH
from tensorbay.client.struct import ROOT_COMMIT_ID
from tensorbay.dataset import Data, Segment
from tensorbay.exception import ResourceNotExistError, StatusError

from .utility import get_dataset_name


class TestCommit:
    def test_get_commit(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1", "test", tag="V1")
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
        assert commit.description == "test"
        assert commit.committer.name
        assert commit.committer.date

        # If not giving commit, get the current commit
        commit = dataset_client.get_commit()
        assert commit.commit_id == commit_2_id
        assert commit.parent_commit_id == commit_1_id
        assert commit.title == "commit-2"
        assert commit.description == ""
        assert commit.committer.name
        assert commit.committer.date

        # Can not create the tag without giving commit in the draft
        dataset_client.create_draft("draft-3")
        with pytest.raises(StatusError):
            dataset_client.get_commit()

        gas_client.delete_dataset(dataset_name)

    def test_get_commit_by_revision(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1", "test", tag="V1")
        commit_1_id = dataset_client.status.commit_id
        dataset_client.create_draft("draft-2")
        dataset_client.commit("commit-2")
        commit_2_id = dataset_client.status.commit_id

        # Get top commit by tag
        commit = dataset_client.get_commit("V1")
        assert commit.commit_id == commit_1_id
        assert commit.parent_commit_id == ROOT_COMMIT_ID
        assert commit.title == "commit-1"
        assert commit.description == "test"
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

        with pytest.raises(ResourceNotExistError):
            dataset_client.get_commit("V2")

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

        # List commits(based on default branch)
        commits = dataset_client.list_commits()
        assert len(commits) == 3
        assert commits[0].commit_id == commit_3_id
        assert commits[1].commit_id == commit_2_id

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

    def test_data_in_draft(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        segment = Segment("segment1")
        path = tmp_path / "sub"
        path.mkdir()
        for i in range(10):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            segment.append(data)

        dataset_client.upload_segment(segment)
        dataset_client.commit("commit-1")
        segment1 = Segment(name="segment1", client=dataset_client)
        assert len(segment1) == 10
        assert segment1[0].get_url()
        assert segment1[0].path == segment[0].target_remote_path

        dataset_client.create_draft("draft-2")
        segment1 = Segment(name="segment1", client=dataset_client)
        assert len(segment1) == 10
        assert segment1[0].get_url()
        assert segment1[0].path == segment[0].target_remote_path

        gas_client.delete_dataset(dataset_name)
