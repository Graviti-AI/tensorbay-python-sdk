#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import os

import ulid

from tensorbay.client.lazy import LazyItem, LazyPage
from tensorbay.dataset import Frame

_FRAME_ID = ulid.from_str("01F29QVWASMNGNA2FZBMZCDEG1")

_FRAME_DATA = {
    "frameId": _FRAME_ID.str,
    "frame": [
        {
            "sensorName": "sensor1",
            "remotePath": "test1.png",
            "timestamp": 1614945883,
            "url": "url1",
            "label": {},
        },
        {
            "sensorName": "sensor2",
            "remotePath": "test2.png",
            "timestamp": 1614945884,
            "url": "url2",
            "label": {},
        },
    ],
}
URL_PAGE: LazyPage[str] = object.__new__(LazyPage)
URL_PAGE.items = (
    LazyItem(URL_PAGE, {frame["sensorName"]: frame["url"] for frame in _FRAME_DATA["frame"]}),
)


class TestFrame:
    def test_init(self):
        frame = Frame()
        assert not hasattr(frame, "frame_id")
        assert frame._data == {}

        frame = Frame(_FRAME_ID)
        assert frame.frame_id == _FRAME_ID
        assert frame._data == {}

    def test_from_response_body(self):
        frame = Frame.from_response_body(_FRAME_DATA, 0, URL_PAGE, cache_path="cache_path")
        assert frame.frame_id == _FRAME_ID
        assert frame["sensor1"].path == "test1.png"
        assert frame["sensor1"].timestamp == 1614945883
        assert frame["sensor1"].url.get() == "url1"
        assert frame["sensor1"].cache_path == os.path.join("cache_path", "test1.png")
        assert frame["sensor2"].path == "test2.png"
        assert frame["sensor2"].timestamp == 1614945884
        assert frame["sensor2"].url.get() == "url2"
        assert frame["sensor2"].cache_path == os.path.join("cache_path", "test2.png")
