#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from pathlib import Path

import pytest

from ..data import Data, RemoteData

_DATA = {"localPath": "test.json", "timestamp": 1614667532, "label": {}}
_REMOTE_DATA = {"remotePath": "test.json", "timestamp": 1614667532, "label": {}}


class TestData:
    def test_init(self):
        local_path = "test.json"
        target_remote_path = "A/test.json"
        timestamp = 1614667532

        data = Data(local_path, target_remote_path=target_remote_path, timestamp=timestamp)
        assert data.path == local_path
        assert data.target_remote_path == target_remote_path
        assert data.timestamp == timestamp

    def test_loads(self):
        data = Data.loads(_DATA)
        assert data.path == _DATA["localPath"]
        assert data.timestamp == _DATA["timestamp"]

    def test_dumps(self):
        data = Data("test.json", timestamp=_DATA["timestamp"])
        assert data.dumps() == _DATA

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
        remote_data = RemoteData(remote_path, timestamp=timestamp, url_getter=lambda x: x)
        assert remote_data.path == remote_path
        assert remote_data.timestamp == timestamp
        assert remote_data.get_url() == remote_path

    def test_get_url(self):
        remote_data = RemoteData("A/test.josn")
        with pytest.raises(ValueError):
            remote_data.get_url()

    def test_loads(self):
        data = RemoteData.loads(_REMOTE_DATA)
        assert data.path == _REMOTE_DATA["remotePath"]
        assert data.timestamp == _REMOTE_DATA["timestamp"]

    def test_dumps(self):
        data = RemoteData("test.json", timestamp=_DATA["timestamp"])
        assert data.dumps() == _REMOTE_DATA
