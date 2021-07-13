#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from .. import LabelType


class TestLabelType:
    def test_init(self):
        assert LabelType.CLASSIFICATION == LabelType("classification")
        assert LabelType.BOX2D == LabelType("box2d")
        assert LabelType.BOX3D == LabelType("box3d")
        assert LabelType.POLYGON == LabelType("polygon")
        assert LabelType.POLYLINE2D == LabelType("polyline2d")
        assert LabelType.KEYPOINTS2D == LabelType("keypoints2d")
        assert LabelType.SENTENCE == LabelType("sentence")
