#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from .. import FusionSegment, Segment

_SEGMENT_DATA = {
    "name": "train",
    "description": "test segment",
    "data": [{"localPath": "test1.png", "label": {}}, {"localPath": "test2.png", "label": {}}],
}
_FUSION_SEGMENT_DATA = {
    "name": "train001",
    "description": "test fusion segment",
    "sensors": [{"type": "CAMERA", "name": "camera"}, {"type": "LIDAR", "name": "lidar"}],
    "frames": [
        {
            "frame": [
                {
                    "sensorName": "camera",
                    "localPath": "camera.png",
                    "timestamp": 1614945883,
                    "label": {},
                },
                {
                    "sensorName": "lidar",
                    "localPath": "lidar.pcd",
                    "timestamp": 1614945884,
                    "label": {},
                },
            ],
        }
    ],
}


class TestSegment:
    def test_loads_dumps(self):
        segment = Segment.loads(_SEGMENT_DATA)
        assert segment.dumps() == _SEGMENT_DATA

    def test_sort(self):
        segment = Segment.loads(_SEGMENT_DATA)
        segment.sort(key=lambda data: data.path, reverse=True)
        assert segment[0].path == _SEGMENT_DATA["data"][-1]["localPath"]


class TestFusionSegment:
    def test_loads_dumps(self):
        fusion_segment = FusionSegment.loads(_FUSION_SEGMENT_DATA)
        assert fusion_segment.dumps() == _FUSION_SEGMENT_DATA
