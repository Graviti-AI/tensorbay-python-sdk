#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import os
from pathlib import Path

import pytest

from tensorbay.dataset.data import Data, RemoteData

_REMOTE_DATA = {
    "remotePath": "test.json",
    "timestamp": 1614667532,
    "label": {},
    "url": "url",
}


class TestData:
    def test_init(self):
        local_path = "test.json"
        target_remote_path = "A/test.json"
        timestamp = 1614667532

        data = Data(local_path, target_remote_path=target_remote_path, timestamp=timestamp)
        assert data.path == local_path
        assert data.target_remote_path == target_remote_path
        assert data.timestamp == timestamp

    def test_get_callback_body(self, tmp_path):
        local_path = tmp_path / "file"
        local_path.write_text("CONTENT")

        timestamp = 1234

        data = Data(str(local_path), timestamp=timestamp)

        assert data.get_callback_body() == {
            "checksum": "238a131a3e8eb98d1fc5b27d882ca40b7618fd2a",
            "fileSize": 7,
            "remotePath": local_path.name,
            "timestamp": timestamp,
        }

    def test_target_remote_path(self):
        target_remote_path = "test2.json"
        data_object = Data("test.json")
        data_object.target_remote_path = target_remote_path
        assert data_object.target_remote_path == target_remote_path

    def test_get_url(self):
        local_relative_path = Path(__file__).relative_to(Path.cwd())
        data = Data(str(local_relative_path))
        assert data.get_url() == local_relative_path.resolve().as_uri()
        data = Data(__file__)
        assert data.get_url() == Path(__file__).resolve().as_uri()


class TestRemoteData:
    def test_init(self):
        remote_path = "A/test.json"
        timestamp = 1614667532
        remote_data = RemoteData(remote_path, timestamp=timestamp, _url_getter=lambda x: x)
        assert remote_data.path == remote_path
        assert remote_data.timestamp == timestamp
        assert remote_data.get_url() == remote_path

    def test_get_url(self):
        remote_data = RemoteData("A/test.josn")
        with pytest.raises(ValueError):
            remote_data.get_url()

    def test_from_response_body(self):
        data = RemoteData.from_response_body(
            _REMOTE_DATA, _url_getter=lambda _: "url", cache_path="cache_path"
        )
        assert data.path == _REMOTE_DATA["remotePath"]
        assert data.timestamp == _REMOTE_DATA["timestamp"]
        assert data.get_url() == "url"
        assert data.cache_path == os.path.join("cache_path", _REMOTE_DATA["remotePath"])
