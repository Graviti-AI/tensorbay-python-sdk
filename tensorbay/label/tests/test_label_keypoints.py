#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from ...geometry import Keypoint2D
from .. import LabeledKeypoints2D

_CATEGORY = "test"
_ATTRIBUTES = {"key": "value"}
_INSTANCE = "12345"

_LABELEDKEYPOINTS2D_DATA = {
    "keypoints2d": [
        {"x": 1, "y": 1, "v": 2},
    ],
    "category": "test",
    "attributes": {"key": "value"},
    "instance": "12345",
}


class TestLabeledKeypoints2D:
    def test_init(self):
        labeledkeypoints2d = LabeledKeypoints2D(
            [(1, 2)], category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert labeledkeypoints2d[0] == Keypoint2D(x=1, y=2)
        assert labeledkeypoints2d.category == _CATEGORY
        assert labeledkeypoints2d.attributes == _ATTRIBUTES
        assert labeledkeypoints2d.instance == _INSTANCE

    def test_loads(self):
        labeledkeypoints2d = LabeledKeypoints2D.loads(_LABELEDKEYPOINTS2D_DATA)

        assert labeledkeypoints2d[0] == Keypoint2D(x=1, y=1, v=2)
        assert labeledkeypoints2d.category == _LABELEDKEYPOINTS2D_DATA["category"]
        assert labeledkeypoints2d.attributes == _LABELEDKEYPOINTS2D_DATA["attributes"]
        assert labeledkeypoints2d.instance == _LABELEDKEYPOINTS2D_DATA["instance"]

    def test_dumps(self):
        labeledkeypoints2d = LabeledKeypoints2D(
            [(1, 1, 2)], category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert labeledkeypoints2d.dumps() == _LABELEDKEYPOINTS2D_DATA
