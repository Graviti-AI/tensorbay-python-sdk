#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay import GAS
from tensorbay.exception import NameConflictError, ResourceNotExistError, StatusError

from .utility import get_dataset_name


class TestSegment:
    def test_create_segment(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)

        with pytest.raises(StatusError):
            dataset_client.create_segment("segment")
        dataset_client.create_draft("draft-1")
        segment_client = dataset_client.create_segment("segment")
        # Cannot create duplicated segment
        with pytest.raises(NameConflictError):
            dataset_client.create_segment("segment")
        assert segment_client.status.is_draft
        assert segment_client.name == "segment"
        dataset_client.get_segment("segment")

        gas_client.delete_dataset(dataset_name)

    def test_get_or_create_segment(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)

        with pytest.raises(StatusError):
            dataset_client.get_or_create_segment("segment")
        dataset_client.create_draft("draft-1")
        segment_client = dataset_client.get_or_create_segment("segment")
        assert segment_client.status.is_draft
        assert segment_client.name == "segment"
        dataset_client.get_segment("segment")

        gas_client.delete_dataset(dataset_name)

    def test_get_or_create_fusion_segment(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, is_fusion=True)

        with pytest.raises(StatusError):
            dataset_client.get_or_create_segment("segment")
        dataset_client.create_draft("draft-1")
        segment_client = dataset_client.get_or_create_segment("segment")
        assert segment_client.status.is_draft
        assert segment_client.name == "segment"
        dataset_client.get_segment("segment")

        gas_client.delete_dataset(dataset_name)

    def test_list_segment_names(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.get_or_create_segment("segment1")
        dataset_client.get_or_create_segment("segment2")

        segments = dataset_client.list_segment_names()
        assert "segment1" in segments
        assert "segment2" in segments
        assert "segment3" not in segments

        gas_client.delete_dataset(dataset_name)

    def test_delete_segment(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.get_or_create_segment("segment1")

        dataset_client.delete_segment("segment1")
        with pytest.raises(ResourceNotExistError):
            dataset_client.get_segment("segment1")

        gas_client.delete_dataset(dataset_name)
