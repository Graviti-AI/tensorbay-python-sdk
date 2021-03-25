#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from .. import Classification, Label, LabeledBox2D, LabelType

_FAILED_DATA = {
    "box2d": [
        {
            "box2d": {"xmin": 1, "ymin": 1, "xmax": 2, "ymax": 2},
        }
    ]
}
_CLASSIFICATION_DATA = {
    "CLASSIFICATION": {"category": "test_categoty", "attributes": {"test_attribute1": "a"}}
}
_BOX2D_DATA = {
    "BOX2D": [
        {
            "box2d": {"xmin": 1, "ymin": 1, "xmax": 2, "ymax": 2},
            "category": "test_categoty",
            "attributes": {"test_attribute1": "a"},
        }
    ]
}


class TestLabelType:
    def test_init(self):
        assert LabelType.CLASSIFICATION == LabelType("classification")
        assert LabelType.BOX2D == LabelType("box2d")
        assert LabelType.BOX3D == LabelType("box3d")
        assert LabelType.POLYGON2D == LabelType("polygon2d")
        assert LabelType.POLYLINE2D == LabelType("polyline2d")
        assert LabelType.KEYPOINTS2D == LabelType("keypoints2d")
        assert LabelType.SENTENCE == LabelType("sentence")


class TestLabel:
    def test_bool(self):
        label = Label()
        assert bool(label) == False

        label.classification = Classification()
        assert bool(label) == True

    def test_eq(self):
        label1 = Label()
        label1.classification = Classification("cat", {"color": "white"})

        label2 = Label()
        label2.classification = Classification("cat", {"color": "white"})

        label3 = Label()
        label3.classification = Classification("cat", {"color": "black"})

        assert label1 == label2
        assert label1 != label3

    def test_loads(self):
        label = Label.loads(_FAILED_DATA)
        assert hasattr(label, "box2d") == False

        label = Label.loads(_CLASSIFICATION_DATA)
        assert label.classification.category == _CLASSIFICATION_DATA["CLASSIFICATION"]["category"]
        assert (
            label.classification.attributes == _CLASSIFICATION_DATA["CLASSIFICATION"]["attributes"]
        )

        label = Label.loads(_BOX2D_DATA)
        box2d_object = label.box2d[0]
        box2d = _BOX2D_DATA["BOX2D"][0]
        assert box2d_object.category == box2d["category"]
        assert box2d_object.attributes == box2d["attributes"]
        assert box2d_object._data == (1, 1, 2, 2)

    def test_dumps(self):
        category = "test_categoty"
        attributes = {"test_attribute1": "a"}
        label = Label()
        label.classification = Classification(category, attributes)
        assert label.dumps() == _CLASSIFICATION_DATA

        label = Label()
        label.box2d = [LabeledBox2D(1, 1, 2, 2, category=category, attributes=attributes)]
        assert label.dumps() == _BOX2D_DATA
