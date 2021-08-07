#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import ulid

from .. import Frame, RemoteData

_FRAME_ID = ulid.from_str("01F29QVWASMNGNA2FZBMZCDEG1")

_FRAME_DATA = {
    "frameId": _FRAME_ID.str,
    "frame": [
        {
            "sensorName": "sensor1",
            "remotePath": "test1.png",
            "timestamp": 1614945883,
            "label": {},
        },
        {
            "sensorName": "sensor2",
            "remotePath": "test2.png",
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

    def test_from_response_body(self):
        frame = Frame.from_response_body(_FRAME_DATA, 0, [{"sensor1": "url1", "sensor2": "url2"}])
        assert frame.frame_id == _FRAME_ID
        assert frame["sensor1"].path == "test1.png"
        assert frame["sensor1"].timestamp == 1614945883
        assert frame["sensor1"].get_url() == "url1"
        assert frame["sensor2"].path == "test2.png"
        assert frame["sensor2"].timestamp == 1614945884
        assert frame["sensor2"].get_url() == "url2"
