#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay.client import GAS
from tensorbay.client.gas import DEFAULT_BRANCH
from tensorbay.client.struct import Draft
from tensorbay.exception import ResourceNotExistError, ResponseError, StatusError

from .utility import get_dataset_name, get_draft_number_by_title


class TestDraft:
    def test_create_draft(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)

        draft_number_1 = dataset_client.create_draft("draft-1", "description")
        assert draft_number_1 == 1
        assert dataset_client.status.is_draft
        assert dataset_client.status.draft_number == draft_number_1
        assert dataset_client.status.commit_id is None
        with pytest.raises(StatusError):
            dataset_client.create_draft("draft-2")
        draft_number = get_draft_number_by_title(dataset_client.list_drafts(), "draft-1")
        assert draft_number_1 == draft_number

        gas_client.delete_dataset(dataset_name)

    def test_list_drafts(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1", "description for draft 1")
        dataset_client.commit("commit-draft-1")
        draft_number_2 = dataset_client.create_draft("draft-2", "description for draft 2")

        # After committing, the draft will be deleted
        with pytest.raises(TypeError):
            get_draft_number_by_title(dataset_client.list_drafts(), "draft-1")

        drafts = dataset_client.list_drafts()
        assert len(drafts) == 1
        assert drafts[0] == Draft(
            draft_number_2, "draft-2", DEFAULT_BRANCH, "OPEN", "description for draft 2"
        )

        with pytest.raises(TypeError):
            get_draft_number_by_title(dataset_client.list_drafts(), "draft-3")

        gas_client.delete_dataset(dataset_name)

    def test_commit_draft(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1")
        dataset_client.create_draft("draft-2")
        dataset_client.commit("commit-2", tag="V1")

        dataset_client.create_draft("draft-3")
        with pytest.raises(ResponseError):
            dataset_client.commit("commit-3", tag="V1")
        dataset_client.commit("commit-3", tag="V2")
        assert not dataset_client.status.is_draft
        assert dataset_client.status.draft_number is None
        assert dataset_client.status.commit_id is not None
        # After committing, the draft will be deleted
        with pytest.raises(TypeError):
            get_draft_number_by_title(dataset_client.list_drafts(), "draft-3")

        gas_client.delete_dataset(dataset_name)

    def test_update_draft(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1", "test", tag="V1")
        dataset_client.create_draft("draft-2")

        dataset_client.checkout("V1")
        dataset_client.create_branch("T123")
        dataset_client.create_draft("draft-3", "description00")
        dataset_client.update_draft(title="draft-4", description="description01")

        draft = dataset_client.get_draft(3)
        assert draft.title == "draft-4"
        assert draft.description == "description01"

        dataset_client.update_draft(2, title="draft-4", description="description02")
        draft = dataset_client.get_draft(2)
        assert draft.title == "draft-4"
        assert draft.description == "description02"

        gas_client.delete_dataset(dataset_name)

    def test_close_draft(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1", "test", tag="V1")
        dataset_client.create_draft("draft-2")

        dataset_client.checkout("V1")
        dataset_client.create_branch("T123")
        dataset_client.create_draft("draft-3")

        dataset_client.close_draft()
        with pytest.raises(ResourceNotExistError):
            dataset_client.get_draft(3)

        dataset_client.close_draft(2)
        with pytest.raises(ResourceNotExistError):
            dataset_client.get_draft(2)

        gas_client.delete_dataset(dataset_name)
