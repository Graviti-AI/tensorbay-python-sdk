#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import os
import time

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


class TestSquashAndMerge:
    def test_squash_and_merge_abort(self, dataset_client):
        draft_number = dataset_client.squash_and_merge(
            "draft-4",
            description="description",
            source_branch_name="dev",
            target_branch_name=DEFAULT_BRANCH,
            strategy="abort",
        )
        time.sleep(5)
        dataset_client.checkout(draft_number=draft_number)
        assert dataset_client.status.branch_name == DEFAULT_BRANCH
        segment_data = dataset_client.get_segment("Segment1").list_data()
        assert len(segment_data) == 4
        for i in range(4):
            data = segment_data[i]
            assert data.path == f"hello{i}.txt"
            assert data.label == Label.loads(LABEL_1)
        dataset_client.checkout(DEFAULT_BRANCH)
        dataset_client.close_draft(draft_number)

    def test_squash_and_merge_override(self, dataset_client):
        draft_number = dataset_client.squash_and_merge(
            "draft-5",
            description="description",
            source_branch_name="dev",
            target_branch_name=DEFAULT_BRANCH,
            strategy="override",
        )
        time.sleep(5)
        dataset_client.checkout(draft_number=draft_number)
        assert dataset_client.status.branch_name == DEFAULT_BRANCH
        segment_data = dataset_client.get_segment("Segment1").list_data()
        assert len(segment_data) == 10
        for i in range(10):
            data = segment_data[i]
            assert data.path == f"hello{i}.txt"
            assert data.label == Label.loads(LABEL_2)
        dataset_client.checkout(DEFAULT_BRANCH)
        dataset_client.close_draft(draft_number)

    def test_squash_and_merge_skip(self, dataset_client):
        draft_number = dataset_client.squash_and_merge(
            "draft-6",
            description="description",
            source_branch_name="dev",
            target_branch_name=DEFAULT_BRANCH,
            strategy="skip",
        )
        time.sleep(5)
        dataset_client.checkout(draft_number=draft_number)
        assert dataset_client.status.branch_name == DEFAULT_BRANCH
        segment_data = dataset_client.get_segment("Segment1").list_data()
        assert len(segment_data) == 10
        for i in range(10):
            data = segment_data[i]
            assert data.path == f"hello{i}.txt"
            if i < 4:
                assert data.label == Label.loads(LABEL_1)
            else:
                assert data.label == Label.loads(LABEL_2)
        dataset_client.checkout(DEFAULT_BRANCH)
        dataset_client.close_draft(draft_number)
