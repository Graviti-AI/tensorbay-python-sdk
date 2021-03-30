#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import json
import os

import pytest

from .. import Dataset, FusionDataset, FusionSegment, Segment
from ..dataset import DatasetBase, Notes

_NOTES_DATA = {
    "isContinuous": True,
}


class TestNotes:
    def test_init(self):
        notes = Notes(True)
        assert notes.is_continuous == True

        notes = Notes()
        assert notes.is_continuous == False

    def test_loads(self):
        notes = Notes.loads(_NOTES_DATA)
        assert notes.is_continuous == _NOTES_DATA["isContinuous"]

    def test_dumps(self):
        notes = Notes(True)
        assert notes.dumps() == _NOTES_DATA


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
