#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest
import ulid

from .. import Data, Frame

_FRAME_ID = ulid.from_str("01F29QVWASMNGNA2FZBMZCDEG1")

_FRAME_DATA = {
    "frameId": _FRAME_ID.str,
    "frame": [
        {
            "sensorName": "sensor1",
            "localPath": "test1.png",
            "timestamp": 1614945883,
            "label": {},
        },
        {
            "sensorName": "sensor2",
            "localPath": "test2.png",
            "timestamp": 1614945884,
            "label": {},
        },
    ],
}


class TestFrame:
    def test_init(self):
        frame = Frame()
        assert not hasattr(frame, "frame_id")
        assert frame._data == {}

        frame = Frame(_FRAME_ID)
        assert frame.frame_id == _FRAME_ID
        assert frame._data == {}

    def test_loads(self):
        frame = Frame.loads(_FRAME_DATA)
        assert frame.frame_id == _FRAME_ID
        assert frame["sensor1"].path == "test1.png"
        assert frame["sensor1"].timestamp == 1614945883
        assert frame["sensor2"].path == "test2.png"
        assert frame["sensor2"].timestamp == 1614945884

    def test_dumps(self):
        frame = Frame(_FRAME_ID)
        frame["sensor1"] = Data("test1.png", timestamp=1614945883)
        frame["sensor2"] = Data("test2.png", timestamp=1614945884)
        assert frame.dumps() == _FRAME_DATA
