#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import os

import pytest

from tensorbay.client import GAS
from tensorbay.client.gas import DEFAULT_BRANCH
from tensorbay.dataset import Data, Dataset
from tensorbay.label import Catalog, Label
from tests.utility import get_dataset_name

CATALOG = {
    "BOX2D": {
        "categories": [
            {"name": "01"},
            {"name": "02"},
            {"name": "03"},
            {"name": "04"},
            {"name": "05"},
            {"name": "06"},
            {"name": "07"},
            {"name": "08"},
            {"name": "09"},
            {"name": "10"},
            {"name": "11"},
            {"name": "12"},
            {"name": "13"},
            {"name": "14"},
            {"name": "15"},
        ],
    }
}

LABEL_1 = {
    "BOX2D": [
        {
            "category": "01",
            "box2d": {"xmin": 639.85, "ymin": 175.24, "xmax": 667.59, "ymax": 200.41},
        }
    ]
}
LABEL_2 = {
    "BOX2D": [
        {
            "category": "02",
            "box2d": {"xmin": 639.85, "ymin": 175.24, "xmax": 667.59, "ymax": 200.41},
        }
    ]
}


@pytest.fixture(scope="class", name="dataset_client")
def init_dataset_client(accesskey, url, tmp_path_factory):
    gas_client = GAS(access_key=accesskey, url=url)
    dataset_name = get_dataset_name()
    dataset_client = gas_client.create_dataset(dataset_name)

    dataset_client.create_draft("draft-1")
    dataset_client.commit("commit-1")

    dataset_client.create_branch("dev")
    dataset = Dataset(name=dataset_name)
    segment = dataset.create_segment("Segment1")
    dataset._catalog = Catalog.loads(CATALOG)
    path = tmp_path_factory.mktemp("sub")
    os.makedirs(path, exist_ok=True)
    for i in range(10):
        local_path = path / f"hello{i}.txt"
        local_path.write_text(f"CONTENT_{i}")
        data = Data(local_path=str(local_path))
        data.label = Label.loads(LABEL_2)
        segment.append(data)
    dataset_client = gas_client.upload_dataset(dataset, branch_name="dev")
    dataset_client.commit("commit-2")

    dataset_client.checkout(DEFAULT_BRANCH)
    dataset = Dataset(name=dataset_name)
    segment = dataset.create_segment("Segment1")
    dataset._catalog = Catalog.loads(CATALOG)
    path = tmp_path_factory.mktemp("sub")
    os.makedirs(path, exist_ok=True)
    for i in range(4):
        local_path = path / f"hello{i}.txt"
        local_path.write_text(f"CONTENT_{i}")
        data = Data(local_path=str(local_path))
        data.label = Label.loads(LABEL_1)
        segment.append(data)
    dataset_client = gas_client.upload_dataset(dataset, branch_name=DEFAULT_BRANCH)
    dataset_client.commit("commit-3")
    yield dataset_client

    gas_client.delete_dataset(dataset_name)


@pytest.fixture(scope="class", name="job", params=["abort", "override", "skip"])
def init_job(dataset_client, request):
    dataset_client.checkout(DEFAULT_BRANCH)
    for draft in dataset_client.list_drafts():
        dataset_client.close_draft(draft.number)

    strategy = request.param
    job = dataset_client.squash_and_merge.create_job(
        draft_title=f"draft-by-{strategy}",
        source_branch_name="dev",
        target_branch_name=DEFAULT_BRANCH,
        strategy=strategy,
        draft_description="description",
    )
    job.abort()
    job.update()
    assert job.status == "ABORTED"
    job.retry()
    job.update()
    assert job.status == "PROCESSING"

    yield job


class TestSquashAndMerge:
    @pytest.mark.xfail(reason="can not retry a job immediately after it is aborted")
    def test_get_job(self, dataset_client, job):
        job_id = job.job_id
        job = dataset_client.squash_and_merge.get_job(job_id)
        assert job.job_id == job_id

    @pytest.mark.xfail(reason="can not retry a job immediately after it is aborted")
    def test_update_job(self, dataset_client, job):
        job = dataset_client.squash_and_merge.get_job(job.job_id)
        job.update(until_complete=True)
        assert job.status == "SUCCESS"

    @pytest.mark.xfail(reason="can not retry a job immediately after it is aborted")
    def test_job_result(self, dataset_client, job):
        job.update()
        dataset_client.checkout(draft_number=job.result.number)
        assert dataset_client.status.branch_name == DEFAULT_BRANCH
        segment_data = dataset_client.get_segment("Segment1").list_data()

        if job.arguments.get("strategy") == "abort":
            assert len(segment_data) == 4
            for i in range(4):
                data = segment_data[i]
                assert data.path == f"hello{i}.txt"
                assert data.label == Label.loads(LABEL_1)

        if job.arguments.get("strategy") == "override":
            assert len(segment_data) == 10
            for i in range(10):
                data = segment_data[i]
                assert data.path == f"hello{i}.txt"
                assert data.label == Label.loads(LABEL_2)

        if job.arguments.get("strategy") == "skip":
            assert len(segment_data) == 10
            for i in range(10):
                data = segment_data[i]
                assert data.path == f"hello{i}.txt"
                if i < 4:
                    assert data.label == Label.loads(LABEL_1)
                else:
                    assert data.label == Label.loads(LABEL_2)

    @pytest.mark.xfail(reason="can not retry a job immediately after it is aborted")
    def test_list_jobs(self, dataset_client):
        jobs = dataset_client.squash_and_merge.list_jobs()
        assert len(jobs) == 3
        for job in jobs:
            dataset_client.squash_and_merge.delete_job(job.job_id)
        jobs = dataset_client.squash_and_merge.list_jobs()
        assert len(jobs) == 0
