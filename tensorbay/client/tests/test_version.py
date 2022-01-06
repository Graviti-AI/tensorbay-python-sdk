#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay.client.dataset import DatasetClient
from tensorbay.client.gas import DEFAULT_BRANCH, DEFAULT_IS_PUBLIC, GAS
from tensorbay.client.job import SquashAndMergeJob
from tensorbay.client.lazy import ReturnGenerator
from tensorbay.client.status import Status
from tensorbay.client.struct import ROOT_COMMIT_ID
from tensorbay.exception import StatusError


class TestVersionControlMixin:
    gas_client = GAS("Accesskey-********************************")
    dataset_client = DatasetClient(
        "test_dataset",
        "12345",
        gas_client,
        status=Status(DEFAULT_BRANCH, commit_id=ROOT_COMMIT_ID),
        alias="",
        is_public=DEFAULT_IS_PUBLIC,
    )


class TestJobMixin:
    gas_client = GAS("Accesskey-********************************")
    dataset_client = DatasetClient(
        "test_dataset",
        "12345",
        gas_client,
        status=Status(DEFAULT_BRANCH, commit_id=ROOT_COMMIT_ID),
        alias="",
        is_public=DEFAULT_IS_PUBLIC,
    )

    def test__create_job(self, mocker, mock_create_job):
        post_data = {
            "title": "test->main(abort)",
            "jobType": "squashAndMerge",
            "arguments": {"title": "draft-1"},
            "description": "12",
        }
        open_api_do, response_data = mock_create_job(mocker)
        response_data.update(
            title=post_data["title"],
            arguments=post_data["arguments"],
            status="QUEUING",
            description=post_data["description"],
        )
        assert response_data == self.dataset_client.squash_and_merge._create_job(
            post_data["title"],
            post_data["jobType"],
            post_data["arguments"],
            post_data["description"],
        )
        open_api_do.assert_called_once_with(
            "POST", "jobs", self.dataset_client.dataset_id, json=post_data
        )

    def test__get_job(self, mocker, mock_get_job):
        job_id = "123"
        open_api_do, response_data = mock_get_job(mocker)
        assert response_data == self.dataset_client.squash_and_merge._get_job(job_id)
        open_api_do.assert_called_once_with("GET", f"jobs/{job_id}", self.dataset_client.dataset_id)

    def test__list_jobs(self, mocker, mock_list_jobs):
        params = {
            "jobType": "squashAndMerge",
            "status": None,
            "offset": 0,
            "limit": 128,
        }
        open_api_do, response_data = mock_list_jobs(mocker)
        assert response_data == self.dataset_client.squash_and_merge._list_jobs(
            params["jobType"], params["status"], params["offset"], params["limit"]
        )
        open_api_do.assert_called_once_with(
            "GET", "jobs", self.dataset_client.dataset_id, params=params
        )


class TestSquashAndMerge(TestJobMixin):
    def test__generate_jobs(self, mocker, mock_list_jobs):
        status, offset, limit = None, 0, 128
        params = {
            "jobType": "squashAndMerge",
            "status": status,
            "offset": offset,
            "limit": limit,
        }
        open_api_do, response_data = mock_list_jobs(mocker)
        job_generator = ReturnGenerator(self.dataset_client.squash_and_merge._generate_jobs())
        assert list(job_generator) == [
            SquashAndMergeJob.from_response_body(
                item,
                dataset_id=self.dataset_client.squash_and_merge._dataset_id,
                client=self.dataset_client.squash_and_merge._client,
                job_updater=self.dataset_client.squash_and_merge._get_job,
                draft_getter=self.dataset_client.squash_and_merge._draft_getter,
            )
            for item in response_data["jobs"]
        ]
        open_api_do.assert_called_once_with(
            "GET", "jobs", self.dataset_client.dataset_id, params=params
        )
        assert job_generator.value == response_data["totalCount"]

    def test_create_job(self, mocker, mock_create_job):
        title, description = "", "12"
        source_branch_name = "branch-1"
        draft_title, draft_description = "draft-1", ""
        strategy = "abort"
        with pytest.raises(StatusError):
            self.dataset_client.squash_and_merge._status.branch_name = None
            self.dataset_client.squash_and_merge.create_job(
                title=title,
                description=description,
                draft_title=draft_title,
                source_branch_name=source_branch_name,
                target_branch_name=None,
                draft_description=draft_description,
                strategy=strategy,
            )
        self.dataset_client._status.checkout(commit_id="commit-1")
        self.dataset_client.squash_and_merge._status.branch_name = "branch-2"
        target_branch_name = "branch-2"
        title = f"{source_branch_name}->{target_branch_name}({strategy})"
        arguments = {
            "title": draft_title,
            "sourceBranchName": source_branch_name,
            "targetBranchName": target_branch_name,
            "strategy": strategy,
        }
        post_data = {
            "title": title,
            "jobType": "squashAndMerge",
            "arguments": arguments,
            "description": description,
        }
        open_api_do, job_info = mock_create_job(mocker)
        job_info.update(title=title, arguments=arguments, status="QUEUING", description=description)
        assert self.dataset_client.squash_and_merge.create_job(
            title=title,
            description=description,
            draft_title=draft_title,
            source_branch_name=source_branch_name,
            target_branch_name=None,
            draft_description=draft_description,
            strategy=strategy,
        ) == SquashAndMergeJob.from_response_body(
            job_info,
            dataset_id=self.dataset_client.squash_and_merge._dataset_id,
            client=self.dataset_client.squash_and_merge._client,
            job_updater=self.dataset_client.squash_and_merge._get_job,
            draft_getter=self.dataset_client.squash_and_merge._draft_getter,
        )
        open_api_do.assert_called_once_with(
            "POST", "jobs", self.dataset_client.dataset_id, json=post_data
        )

    def test_get_job(self, mocker, mock_get_job):
        job_id = "123"
        open_api_do, job_info = mock_get_job(mocker)
        assert self.dataset_client.squash_and_merge.get_job(
            job_id
        ) == SquashAndMergeJob.from_response_body(
            job_info,
            dataset_id=self.dataset_client.squash_and_merge._dataset_id,
            client=self.dataset_client.squash_and_merge._client,
            job_updater=self.dataset_client.squash_and_merge._get_job,
            draft_getter=self.dataset_client.squash_and_merge._draft_getter,
        )
        open_api_do.assert_called_once_with("GET", f"jobs/{job_id}", self.dataset_client.dataset_id)

    def test_list_jobs(self, mocker, mock_list_jobs):
        status, offset, limit = None, 0, 128
        params = {
            "jobType": "squashAndMerge",
            "status": status,
            "offset": offset,
            "limit": limit,
        }
        open_api_do, response_data = mock_list_jobs(mocker)
        assert list(self.dataset_client.squash_and_merge.list_jobs(status)) == [
            SquashAndMergeJob.from_response_body(
                item,
                dataset_id=self.dataset_client.squash_and_merge._dataset_id,
                client=self.dataset_client.squash_and_merge._client,
                job_updater=self.dataset_client.squash_and_merge._get_job,
                draft_getter=self.dataset_client.squash_and_merge._draft_getter,
            )
            for item in response_data["jobs"]
        ]
        open_api_do.assert_called_once_with(
            "GET", "jobs", self.dataset_client.dataset_id, params=params
        )
