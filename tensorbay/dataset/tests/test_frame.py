#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from ...geometry import Transform3D
from .. import Frame

_FRAME_DATA = {
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
    def test_loads_dumps(self):
        frame = Frame.loads(_FRAME_DATA)
        assert frame.dumps() == _FRAME_DATA
