#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay.client import GAS
from tensorbay.client.gas import DEFAULT_BRANCH
from tensorbay.exception import (
    InvalidParamsError,
    ResourceNotExistError,
    ResponseError,
    StatusError,
)

from .utility import get_dataset_name


class TestDraft:
    def test_create_draft(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)

        draft_1_number = dataset_client.create_draft(
            "draft-1", "description", branch_name=DEFAULT_BRANCH
        )
        assert draft_1_number == 1

        # Creating more than 1 draft on one branch and one accesskey is not allowed
        with pytest.raises(InvalidParamsError):
            dataset_client.create_draft("draft-2", "description", branch_name=DEFAULT_BRANCH)

        dataset_client.get_draft(draft_1_number)

        gas_client.delete_dataset(dataset_name)

    def test_create_draft_on_other_branch(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1")
        dataset_client.create_branch("dev")

        # Creating the draft on branch "dev"
        draft_2_number = dataset_client.create_draft("draft-2", "description-2", branch_name="dev")
        assert draft_2_number == 2
        draft_get = dataset_client.get_draft(draft_2_number)
        assert draft_get.branch_name == "dev"

        # Creating the draft on DEFAULT BRANCH
        draft_3_number = dataset_client.create_draft(
            "draft-3", "description-3", branch_name=DEFAULT_BRANCH
        )
        assert draft_3_number == 3
        draft_get = dataset_client.get_draft(draft_3_number)
        assert draft_get.branch_name == DEFAULT_BRANCH

        gas_client.delete_dataset(dataset_name)

    def test_get_draft(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        draft_1_number = dataset_client.create_draft("draft-1", "description-1")

        draft_get = dataset_client.get_draft(draft_1_number)
        assert draft_get.number == 1
        assert draft_get.title == "draft-1"
        assert draft_get.branch_name == DEFAULT_BRANCH
        assert draft_get.description == "description-1"
        assert draft_get.status == "OPEN"

        with pytest.raises(ResourceNotExistError):
            dataset_client.get_draft(2)

        gas_client.delete_dataset(dataset_name)

    def test_list_drafts(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1", "description-1")
        dataset_client.commit("commit-1")
        dataset_client.create_draft("draft-2", "description-2")
        dataset_client.checkout(revision=DEFAULT_BRANCH)
        dataset_client.close_draft(2)
        dataset_client.create_draft("draft-3", "description-3")
        dataset_client.checkout(revision=DEFAULT_BRANCH)
        dataset_client.create_branch("dev")
        dataset_client.create_draft("draft-4", "description-4", branch_name="dev")

        # After committing, the draft will be deleted
        drafts_get_open = dataset_client.list_drafts(branch_name=DEFAULT_BRANCH)
        assert len(drafts_get_open) == 1
        assert drafts_get_open[0].number == 3

        drafts_get_closed = dataset_client.list_drafts(status="CLOSED", branch_name=DEFAULT_BRANCH)
        assert len(drafts_get_closed) == 1
        assert drafts_get_closed[0].number == 2

        drafts_get_commited = dataset_client.list_drafts(
            status="COMMITTED", branch_name=DEFAULT_BRANCH
        )
        assert len(drafts_get_commited) == 1
        assert drafts_get_commited[0].number == 1

        drafts_get_all = dataset_client.list_drafts(status="ALL", branch_name=DEFAULT_BRANCH)
        assert len(drafts_get_all) == 3

        drafts_get_dev_open = dataset_client.list_drafts(branch_name="dev")
        assert len(drafts_get_dev_open) == 1
        assert drafts_get_dev_open[0].number == 4

        drafts_get = dataset_client.list_drafts()
        assert len(drafts_get) == 2
        assert drafts_get[0].number == 3
        assert drafts_get[1].number == 4

        gas_client.delete_dataset(dataset_name)

    def test_commit_draft(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.commit("commit-1")
        dataset_client.create_draft("draft-2")
        dataset_client.commit("commit-2", tag="V2")

        # Committing the draft with the duplicated tag is not allowed
        dataset_client.create_draft("draft-3")
        with pytest.raises(ResponseError):
            dataset_client.commit("commit-3", tag="V2")

        dataset_client.commit("commit-3", tag="V3")

        # After committing, the draft will be deleted
        with pytest.raises(ResourceNotExistError):
            dataset_client.get_draft(3)

        gas_client.delete_dataset(dataset_name)

    def test_update_draft(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")

        dataset_client.update_draft(1, title="draft-updated", description="description-updated")
        draft = dataset_client.get_draft(1)
        assert draft.title == "draft-updated"
        assert draft.description == "description-updated"

        gas_client.delete_dataset(dataset_name)

    def test_close_draft(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")

        # Closing the current draft is not allowed
        with pytest.raises(StatusError):
            dataset_client.close_draft(1)

        dataset_client.checkout(revision=DEFAULT_BRANCH)
        dataset_client.close_draft(1)

        with pytest.raises(ResourceNotExistError):
            dataset_client.get_draft(1)

        gas_client.delete_dataset(dataset_name)
