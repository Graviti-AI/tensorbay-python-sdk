#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import json
import os
from typing import KeysView

import pytest

from tensorbay.dataset import Dataset, FusionDataset, FusionSegment, Segment
from tensorbay.dataset.dataset import DatasetBase, Notes

_NOTES_DATA = {
    "isContinuous": True,
    "binPointCloudFields": ["X", "Y", "Z", "Intensity", "Ring"],
}


class TestNotes:
    def test_init(self):
        notes = Notes(True)
        assert notes.is_continuous == True

        notes = Notes()
        assert notes.is_continuous == False
        assert notes.bin_point_cloud_fields == None

        notes = Notes(True, _NOTES_DATA["binPointCloudFields"])
        assert notes.is_continuous == True
        assert notes.bin_point_cloud_fields == _NOTES_DATA["binPointCloudFields"]

    def test_keys(self):
        notes = Notes()
        assert notes.keys() == KeysView(["is_continuous", "bin_point_cloud_fields"])

        notes = Notes(True, _NOTES_DATA["binPointCloudFields"])
        assert notes.keys() == KeysView(["is_continuous", "bin_point_cloud_fields"])

    def test_getitem(self):
        notes = Notes()
        assert notes["is_continuous"] == False
        assert notes["bin_point_cloud_fields"] == None

    def test_loads(self):
        notes = Notes.loads(_NOTES_DATA)
        assert notes.is_continuous == _NOTES_DATA["isContinuous"]

    def test_dumps(self):
        notes = Notes(True, ["X", "Y", "Z", "Intensity", "Ring"])
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

    def test_getitem(self):
        dataset = DatasetBase("test_name")
        train_segment = Segment("train")
        test_segment = Segment("test")
        dataset.add_segment(train_segment)
        dataset.add_segment(test_segment)
        assert test_segment is dataset[0] is dataset["test"]
        assert train_segment is dataset[1] is dataset["train"]

        with pytest.raises(IndexError):
            dataset[2]
        with pytest.raises(KeyError):
            dataset["unknown"]

    def test_delitem(self):
        dataset = DatasetBase("test_name")
        segments = [Segment(str(i)) for i in range(5)]
        for segment in segments:
            dataset.add_segment(segment)

        del segments[1:3]
        del dataset[1:3]
        assert len(dataset) == len(segments)
        for dataset_segment, segment in zip(dataset, segments):
            assert dataset_segment is segment

        del segments[1]
        del dataset[1]
        assert len(dataset) == len(segments)
        for dataset_segment, segment in zip(dataset, segments):
            assert dataset_segment is segment

        del segments[segments.index(dataset["4"])]
        del dataset["4"]
        assert len(dataset) == len(segments)
        for dataset_segment, segment in zip(dataset, segments):
            assert dataset_segment is segment

        del dataset[100:200]
        assert len(dataset) == len(segments)
        for dataset_segment, segment in zip(dataset, segments):
            assert dataset_segment is segment

        with pytest.raises(IndexError):
            del dataset[100]

        with pytest.raises(KeyError):
            del dataset["100"]

    def test_contains(self):
        dataset = DatasetBase("test_name")
        keys = ("test", "train")
        for key in keys:
            dataset.add_segment(Segment(key))

        for key in keys:
            assert key in dataset

        assert "val" not in dataset
        assert 100 not in dataset

    def test_keys(self):
        dataset = DatasetBase("test_name")
        keys = ("test", "train")
        for key in keys:
            dataset.add_segment(Segment(key))
        assert dataset.keys() == keys


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
