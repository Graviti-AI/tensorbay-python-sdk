#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from .. import Classification, Label, LabeledBox2D, LabelType


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

        contents_failed = {"classification": {"category": "cat"}}
        label = Label.loads(contents_failed)
        assert hasattr(label, "classification") == False

        contents = {
            "CLASSIFICATION": {"category": "cat", "attributes": {"gender": "male"}},
            "BOX2D": [
                {
                    "box2d": {"xmin": 1, "ymin": 1, "xmax": 2, "ymax": 2},
                    "category": "dog",
                    "attributes": {"gender": "female"},
                }
            ],
        }
        label = Label.loads(contents)
        assert label.classification.category == "cat"
        assert label.classification.attributes == {"gender": "male"}

        assert label.box2d[0].category == "dog"
        assert label.box2d[0].attributes == {"gender": "female"}
        assert label.box2d[0]._data == (1, 1, 2, 2)

    def test_dumps(self):
        contents = {
            "CLASSIFICATION": {"category": "cat", "attributes": {"gender": "male"}},
            "BOX2D": [
                {
                    "box2d": {"xmin": 1, "ymin": 1, "xmax": 2, "ymax": 2},
                    "category": "dog",
                    "attributes": {"gender": "female"},
                }
            ],
        }

        label = Label()
        label.classification = Classification.loads(contents["CLASSIFICATION"])
        label.box2d = [LabeledBox2D.loads(contents["BOX2D"][0])]
        assert label.dumps() == contents
