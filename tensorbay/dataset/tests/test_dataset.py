#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import json
import os

from .. import Dataset, FusionDataset, FusionSegment, Segment
from ..dataset import DatasetBase


class TestDatasetBase:
    def test_len(self):
        dataset = DatasetBase("test_name")
        dataset.add_segment(Segment("train"))
        assert len(dataset) == 1

    def test_add_and_getitem(self):
        dataset = DatasetBase("test_name")
        segment = Segment("train")
        dataset.add_segment(segment)
        assert dataset[0] is segment

    def test_is_continues(self):
        dataset = DatasetBase("test_name")
        assert dataset.is_continuous == False

        dataset = DatasetBase("test_name", True)
        assert dataset.is_continuous == True

    def test_load_catalog(self):
        catalog_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "opendataset", "HeadPoseImage", "catalog.json"
        )
        dataset = DatasetBase("test_name")
        dataset.load_catalog(catalog_path)
        with open(catalog_path) as fp:
            catalog = json.load(fp)
        assert dataset.catalog.dumps() == catalog

    def test_get_segment_by_name(self):
        dataset = DatasetBase("test_name")
        segment = Segment("train")
        dataset.add_segment(segment)
        assert segment is dataset.get_segment_by_name("train")


class TestDataset:
    def test_create_segment(self):
        dataset = Dataset("test_name")
        segment = dataset.create_segment("train")
        assert segment.name == "train"
        assert isinstance(segment, Segment)


class TestFusionDataset:
    def test_create_fusion_segment(self):
        dataset = FusionDataset("test_name")
        segment = dataset.create_segment("train")
        assert segment.name == "train"
        assert isinstance(segment, FusionSegment)
