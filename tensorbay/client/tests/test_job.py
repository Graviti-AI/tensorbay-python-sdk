#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from tensorbay.client.dataset import DatasetClient
from tensorbay.client.gas import DEFAULT_BRANCH, GAS
from tensorbay.client.job import Job, SquashAndMergeJob
from tensorbay.client.status import Status
from tensorbay.client.struct import ROOT_COMMIT_ID


class TestJob:
    gas_client = GAS("Accesskey-********************************")
    dataset_client = DatasetClient(
        "test_dataset",
        "12345",
        gas_client,
        status=Status(DEFAULT_BRANCH, commit_id=ROOT_COMMIT_ID),
        alias="",
        is_public=True,
    )
    job = Job(
        client=dataset_client.squash_and_merge._client,
        dataset_id=dataset_client.dataset_id,
        job_updater=dataset_client.squash_and_merge._get_job,
        title="test->main(abort)",
        job_id="123",
        job_type="squashAndMerge",
        arguments={"title": "draft-1"},
        created_at=1,
        started_at=2,
        finished_at=3,
        status="SUCCESS",
        error_message="",
        result={"draftNumber": 3},
        description="12",
    )

    def test_update(self, mocker, mock_get_job):
        open_api_do, [_, final_responce] = mock_get_job(mocker, until_complete=True)
        self.job.update(until_complete=True)
        assert self.job.started_at == final_responce["startedAt"]
        assert self.job.finished_at == final_responce["finishedAt"]
        assert self.job.status == final_responce["status"]
        assert self.job.error_message == final_responce["errorMessage"]
        assert self.job._result == final_responce.get("result")
        params = {"jobType": "squashAndMerge"}
        open_api_do.assert_called_with(
            "GET", f"jobs/{self.job.job_id}", self.dataset_client.dataset_id, params=params
        )


class TestSquashAndMergeJob:
    gas_client = GAS("Accesskey-********************************")
    dataset_client = DatasetClient(
        "test_dataset",
        "12345",
        gas_client,
        status=Status(DEFAULT_BRANCH, commit_id=ROOT_COMMIT_ID),
        alias="",
        is_public=True,
    )
    squash_and_merge_job1 = SquashAndMergeJob(
        client=dataset_client.squash_and_merge._client,
        dataset_id=dataset_client.dataset_id,
        job_updater=dataset_client.squash_and_merge._get_job,
        draft_getter=dataset_client.get_draft,
        title="test->main(abort)",
        job_id="234",
        job_type="squashAndMerge",
        arguments={"title": "draft-1"},
        created_at=1,
        started_at=None,
        finished_at=None,
        status="QUEUEING",
        error_message="",
        result=None,
        description="12",
    )
    squash_and_merge_job2 = SquashAndMergeJob(
        client=dataset_client.squash_and_merge._client,
        dataset_id=dataset_client.dataset_id,
        job_updater=dataset_client.squash_and_merge._get_job,
        draft_getter=dataset_client.get_draft,
        title="test->main(abort)",
        job_id="123",
        job_type="squashAndMerge",
        arguments={"title": "draft-1"},
        created_at=1,
        started_at=2,
        finished_at=3,
        status="SUCCESS",
        error_message="",
        result={"draftNumber": 1},
        description="12",
    )

    def test_result(self, mocker, mock_list_drafts):
        list_drafts, drafts_list = mock_list_drafts(mocker, "main")
        assert self.squash_and_merge_job1.result is None
        draft_numbers = (item.number for item in drafts_list)
        assert self.squash_and_merge_job2.result.number in draft_numbers
