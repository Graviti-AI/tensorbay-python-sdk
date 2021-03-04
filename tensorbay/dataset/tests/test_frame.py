#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from ...geometry import Transform3D
from .. import Frame

_FRAME_DATA = {
    "frame": {
        "sensor1": {"localPath": "test1.png", "label": {}},
        "sensor2": {"localPath": "test2.png", "label": {}},
    },
}


class TestFrame:
    def test_loads_dumps(self):
        frame = Frame.loads(_FRAME_DATA)
        assert frame.dumps() == _FRAME_DATA
