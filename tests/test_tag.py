#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay import GAS
from tensorbay.client.struct import ROOT_COMMIT_ID
from tensorbay.exception import ResourceNotExistError, ResponseError, StatusError

from .utility import get_dataset_name


class TestTag:
    def test_create_tag(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1", "test", tag="V1")

        # Can create more than one tag for one commit
        dataset_client.create_tag("V11")

        # Can not create duplicated tag
        with pytest.raises(ResponseError):
            dataset_client.create_tag("V11")

        dataset_client.create_draft("draft-2")
        dataset_client.commit("commit-2")
        commit_2_id = dataset_client.status.commit_id
        dataset_client.create_draft("draft-3")

        # Can not create the tag without giving commit in the draft status
        with pytest.raises(StatusError):
            dataset_client.create_tag("V2")
        # Create the tag with giving commit in the draft status
        dataset_client.create_tag("V2", revision=commit_2_id)

        dataset_client.commit("commit-3")
        commit_3_id = dataset_client.status.commit_id
        dataset_client.create_tag("V3")

        # V1 points to commit 1
        tag1 = dataset_client.get_tag("V1")
        assert tag1.name == "V1"
        assert tag1.parent_commit_id == ROOT_COMMIT_ID

        # V2 points to commit 2
        tag2 = dataset_client.get_tag("V2")
        assert tag2.name == "V2"
        assert tag2.commit_id == commit_2_id

        # V3 points to commit 2
        tag3 = dataset_client.get_tag("V3")
        assert tag3.name == "V3"
        assert tag3.commit_id == commit_3_id
        assert tag3.parent_commit_id == commit_2_id

        gas_client.delete_dataset(dataset_name)

    def test_get_tag(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1", "test", tag="V1")
        commit_1_id = dataset_client.status.commit_id

        tag = dataset_client.get_tag("V1")
        assert tag.name == "V1"
        assert tag.commit_id == commit_1_id
        assert tag.parent_commit_id == ROOT_COMMIT_ID
        assert tag.title == "commit-1"
        assert tag.description == "test"
        assert tag.committer.name
        assert tag.committer.date

        # Can not get a non-exist tag
        with pytest.raises(ResourceNotExistError):
            dataset_client.get_tag("V2")

        dataset_client.create_draft("draft-2")
        dataset_client.commit("commit-2", "test", tag="V2")
        commit_2_id = dataset_client.status.commit_id

        tag = dataset_client.get_tag("V2")
        assert tag.name == "V2"
        assert tag.commit_id == commit_2_id
        assert tag.parent_commit_id == commit_1_id
        assert tag.title == "commit-2"
        assert tag.description == "test"
        assert tag.committer.name
        assert tag.committer.date

        gas_client.delete_dataset(dataset_name)

    def test_list_tags(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1", tag="V1")
        dataset_client.create_draft("draft-2")
        dataset_client.commit("commit-2", tag="V2")
        dataset_client.create_tag("A1")

        tags = dataset_client.list_tags()
        # list by tag name
        assert tags[0].name == "A1"
        assert tags[1].name == "V1"
        assert tags[2].name == "V2"

        gas_client.delete_dataset(dataset_name)

    def test_delete_tag(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1", tag="V1")

        dataset_client.delete_tag("V1")

        with pytest.raises(ResourceNotExistError):
            dataset_client.get_tag("V1")

        gas_client.delete_dataset(dataset_name)
