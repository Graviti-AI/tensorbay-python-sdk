#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from ...geometry import (
    Box2D,
    Box3D,
    Keypoint2D,
    Keypoints2D,
    Polygon2D,
    Polyline2D,
    Quaternion,
    Transform3D,
    Vector2D,
    Vector3D,
)
from .. import (
    Classification,
    LabeledBox2D,
    LabeledBox3D,
    LabeledKeypoints2D,
    LabeledPolygon2D,
    LabeledPolyline2D,
    LabeledSentence,
    LabelType,
    Word,
)

_CATEGORY = "None"
_ATTRIBUTES = {"key": "value"}
_INSTANCE = "tracking ID"

_INITIAL_4x4_TRANSFORM_MATRIX = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

_INITIAL_3x4_TRANSFORM_MATRIX = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

_CLASSIFICATION_DATA = {"category": "car", "attributes": {"name": "Lexus"}}

_LABELEDBOX2D_DATA = {
    "box2d": {"xmin": 1, "ymin": 0, "xmax": 4, "ymax": 2},
    "category": "pedestrians",
    "attributes": {"name": "pose"},
    "instance": "b1c66a42e22c4d75",
}

_LABELEDBOX3D_DATA = {
    "box3d": {
        "translation": {"x": 1, "y": 2, "z": 3},
        "rotation": {"w": 1, "x": 0, "y": 3, "z": 0},
        "size": {"x": 1, "y": 2, "z": 0},
    },
    "category": "car",
    "attributes": {"location": "street"},
    "instance": "b1c66a42e22c4d75",
}

_LABELEDPOLYGON2D_DATA = {
    "polygon2d": [
        {"x": 1, "y": 2},
    ],
    "category": "keypoints",
    "attributes": {"visibility": 0},
    "instance": "b1c66a42e22c4d89",
}

_LABELEDPOLYLINE2D_DATA = {
    "polyline2d": [{"x": 1, "y": 2}],
    "category": "lane",
    "attributes": {"laneDirection": "vertical"},
    "instance": "a1c66a42e22c4d89",
}

_WORD_DATA = {"text": "Hello, World", "begin": 0, "end": 0}

_LABELEDSENTENCE_DATA = {
    "sentence": [{"text": "qi1shi2", "begin": 0, "end": 0}],
    "spell": [{"text": "qi1", "begin": 0, "end": 0}],
    "phone": [{"text": "q", "begin": 0, "end": 0}],
    "attributes": {"name": "patch number"},
}

_LABELEDKEYPOINTS2D_DATA = {
    "keypoints2d": [
        {"x": 1, "y": 1, "v": 2},
    ],
    "category": "Animal",
    "attributes": {"name": "bird"},
    "instance": "a1c66a42e22c4d89",
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


class TestClassification:
    def test_init(self):
        classification = Classification(category=_CATEGORY, attributes=_ATTRIBUTES)

        assert classification.category == _CATEGORY
        assert classification.attributes == _ATTRIBUTES

    def test_loads(self):
        classification = Classification.loads(_CLASSIFICATION_DATA)

        assert classification.category == _CLASSIFICATION_DATA["category"]
        assert classification.attributes == _CLASSIFICATION_DATA["attributes"]

    def test_dumps(self):
        category = "car"
        attributes = {"name": "Lexus"}

        classification = Classification(category=category, attributes=attributes)

        assert classification.dumps() == _CLASSIFICATION_DATA


class TestLabeledBox2D:
    def test_init(self):
        x, y, width, height = 1, 2, 3, 4
        xmin, xmax, ymin, ymax = 1, 2, 4, 6

        labeledbox2d = LabeledBox2D(
            category=_CATEGORY,
            attributes=_ATTRIBUTES,
            instance=_INSTANCE,
            x=x,
            y=y,
            width=width,
            height=height,
        )

        assert LabeledBox2D(None) == LabeledBox2D(0, 0, 0, 0)
        assert LabeledBox2D([0, 0, 0, 0]) == LabeledBox2D(0, 0, 0, 0)
        assert LabeledBox2D(x=0, y=0, width=0, height=0) == LabeledBox2D(0, 0, 0, 0)

        assert labeledbox2d.category == _CATEGORY
        assert labeledbox2d.attributes == _ATTRIBUTES
        assert labeledbox2d.instance == _INSTANCE

        assert labeledbox2d[0] == xmin
        assert labeledbox2d[1] == xmax
        assert labeledbox2d[2] == ymin
        assert labeledbox2d[3] == ymax

    def test_loads(self):
        labeledbox2d = LabeledBox2D.loads(_LABELEDBOX2D_DATA)

        assert labeledbox2d.category == _LABELEDBOX2D_DATA["category"]
        assert labeledbox2d.attributes == _LABELEDBOX2D_DATA["attributes"]
        assert labeledbox2d.instance == _LABELEDBOX2D_DATA["instance"]

        assert labeledbox2d[0] == _LABELEDBOX2D_DATA["box2d"]["xmin"]
        assert labeledbox2d[1] == _LABELEDBOX2D_DATA["box2d"]["ymin"]
        assert labeledbox2d[2] == _LABELEDBOX2D_DATA["box2d"]["xmax"]
        assert labeledbox2d[3] == _LABELEDBOX2D_DATA["box2d"]["ymax"]

    def test_dumps(self):
        category = "pedestrians"
        attributes = {"name": "pose"}
        instance = "b1c66a42e22c4d75"

        labeledbox2d = LabeledBox2D(
            category=category,
            attributes=attributes,
            instance=instance,
            x=1,
            y=0,
            width=3,
            height=2,
        )

        assert labeledbox2d.dumps() == _LABELEDBOX2D_DATA


class TestLabeledBox3D:
    def test_init(self):
        translation = Vector3D(0, 0, 0)
        rotation = Quaternion(1, 0, 0, 0)
        size = Vector3D(0, 0, 0)
        transform = Transform3D(translation=translation, rotation=rotation)

        labeledbox3d = LabeledBox3D(
            transform, category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert LabeledBox3D(None) == LabeledBox3D(transform)
        assert LabeledBox3D(None) == LabeledBox3D(
            translation=translation, rotation=rotation, size=size
        )
        assert LabeledBox3D(_INITIAL_3x4_TRANSFORM_MATRIX) == LabeledBox3D(
            translation=translation, rotation=rotation, size=size
        )
        assert LabeledBox3D(_INITIAL_4x4_TRANSFORM_MATRIX) == LabeledBox3D(
            translation=translation, rotation=rotation, size=size
        )

        assert labeledbox3d.translation == translation
        assert labeledbox3d.rotation == rotation
        assert labeledbox3d.size == size
        assert labeledbox3d.category == _CATEGORY
        assert labeledbox3d.attributes == _ATTRIBUTES
        assert labeledbox3d.instance == _INSTANCE

    def test_rmul(self):
        category = "car"
        attributes = {"name": "Toyota"}
        instance = "12"
        translation = [1, 2, 3]
        rotation = Quaternion(0, 1, 0, 0)
        transform = Transform3D(translation=translation, rotation=rotation)

        labeledbox3d = LabeledBox3D(
            transform, category=category, attributes=attributes, instance=instance
        )

        assert labeledbox3d.__rmul__(transform).category == category
        assert labeledbox3d.__rmul__(transform).attributes == attributes
        assert labeledbox3d.__rmul__(transform).instance == instance

        assert labeledbox3d.__rmul__(1) == NotImplemented

    def test_loads(self):
        labeledbox3d = LabeledBox3D.loads(_LABELEDBOX3D_DATA)

        assert labeledbox3d.category == _LABELEDBOX3D_DATA["category"]
        assert labeledbox3d.attributes == _LABELEDBOX3D_DATA["attributes"]
        assert labeledbox3d.instance == _LABELEDBOX3D_DATA["instance"]

        assert labeledbox3d.translation == Vector3D(1, 2, 3)
        assert labeledbox3d.rotation == Quaternion(1, 0, 3, 0)
        assert labeledbox3d.size == Vector3D(1, 2, 0)

    def test_dumps(self):
        category = "car"
        attributes = {"location": "street"}
        instance = "b1c66a42e22c4d75"
        translation = [1, 2, 3]
        rotation = Quaternion(1, 0, 3, 0)
        size = [1, 2, 0]
        transform = Transform3D(translation=translation, rotation=rotation)

        labeledbox3d = LabeledBox3D(
            transform, size=size, category=category, attributes=attributes, instance=instance
        )

        assert labeledbox3d.dumps() == _LABELEDBOX3D_DATA


class TestLabeledPolygon2D:
    def test_init(self):

        assert LabeledPolygon2D([None]) == LabeledPolygon2D([(0, 0)])
        assert LabeledPolygon2D([0, 0]) == LabeledPolygon2D([(0, 0), (0, 0)])

        labeledpolygon2d = LabeledPolygon2D(
            [(0, 0)], category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert labeledpolygon2d[0] == Vector2D(0, 0)
        assert labeledpolygon2d.category == _CATEGORY
        assert labeledpolygon2d.attributes == _ATTRIBUTES
        assert labeledpolygon2d.instance == _INSTANCE

    def test_loads(self):
        labeledpolygon2d = LabeledPolygon2D.loads(_LABELEDPOLYGON2D_DATA)

        assert labeledpolygon2d[0] == Vector2D(1, 2)
        assert labeledpolygon2d.category == _LABELEDPOLYGON2D_DATA["category"]
        assert labeledpolygon2d.attributes == _LABELEDPOLYGON2D_DATA["attributes"]
        assert labeledpolygon2d.instance == _LABELEDPOLYGON2D_DATA["instance"]

    def test_dumps(self):
        category = "keypoints"
        attributes = {"visibility": 0}
        instance = "b1c66a42e22c4d89"

        labeledpolygon2d = LabeledPolygon2D(
            [(1, 2)], category=category, attributes=attributes, instance=instance
        )

        assert labeledpolygon2d.dumps() == _LABELEDPOLYGON2D_DATA


class TestLabeledPolyline2D:
    def test_init(self):
        assert LabeledPolyline2D([None]) == LabeledPolyline2D([0])
        assert LabeledPolyline2D([0, 0]) == LabeledPolyline2D([(0, 0), (0, 0)])

        labeledpolyline2d = LabeledPolyline2D(
            [0], category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert labeledpolyline2d[0] == Vector2D(0, 0)
        assert labeledpolyline2d.category == _CATEGORY
        assert labeledpolyline2d.attributes == _ATTRIBUTES
        assert labeledpolyline2d.instance == _INSTANCE

    def test_loads(self):
        labeledpolygonline2d = LabeledPolyline2D.loads(_LABELEDPOLYLINE2D_DATA)

        assert labeledpolygonline2d[0] == Vector2D(1, 2)
        assert labeledpolygonline2d.category == _LABELEDPOLYLINE2D_DATA["category"]
        assert labeledpolygonline2d.attributes == _LABELEDPOLYLINE2D_DATA["attributes"]
        assert labeledpolygonline2d.instance == _LABELEDPOLYLINE2D_DATA["instance"]

    def test_dumps(self):
        category = "lane"
        attributes = {"laneDirection": "vertical"}
        instance = "a1c66a42e22c4d89"

        labeledpolygonline2d = LabeledPolyline2D(
            [(1, 2)], category=category, attributes=attributes, instance=instance
        )

        assert labeledpolygonline2d.dumps() == _LABELEDPOLYLINE2D_DATA


class TestWord:
    def test_init(self):
        text = "Hello, World"
        begin = 0
        end = 0

        word = Word(text=text, begin=begin, end=end)

        assert word.text == text
        assert word.begin == begin
        assert word.end == end

    def test_loads(self):
        word = Word.loads(_WORD_DATA)

        assert word.text == "Hello, World"
        assert word.begin == 0
        assert word.end == 0

    def test_dumps(self):
        text = "Hello, World"
        begin = 0
        end = 0

        word = Word(text=text, begin=begin, end=end)

        assert word.dumps() == _WORD_DATA


class TestLabeledSentence:
    def test_init(self):
        begin, end = 0, 0

        sentence = [Word(text="qi1shi2", begin=begin, end=end)]
        spell = [Word(text="qi1", begin=begin, end=end)]
        phone = [Word(text="q", begin=begin, end=end)]
        attributes = {"name": "patch number"}

        labeledsentence = LabeledSentence(
            sentence=sentence, spell=spell, phone=phone, attributes=attributes
        )

        assert labeledsentence.sentence == list(sentence)
        assert labeledsentence.spell == list(spell)
        assert labeledsentence.phone == list(phone)

    def test__load_word(self):
        sentence = LabeledSentence._load_word(_LABELEDSENTENCE_DATA["sentence"])
        spell = LabeledSentence._load_word(_LABELEDSENTENCE_DATA["spell"])
        phone = LabeledSentence._load_word(_LABELEDSENTENCE_DATA["phone"])

        assert sentence[0].text == "qi1shi2"
        assert sentence[0].begin == 0
        assert sentence[0].end == 0

        assert spell[0].text == "qi1"
        assert spell[0].begin == 0
        assert spell[0].end == 0

        assert phone[0].text == "q"
        assert phone[0].begin == 0
        assert phone[0].end == 0

    def test_loads(self):
        labeledsentence = LabeledSentence.loads(_LABELEDSENTENCE_DATA)

        assert labeledsentence.sentence[0].text == _LABELEDSENTENCE_DATA["sentence"][0]["text"]
        assert labeledsentence.sentence[0].begin == _LABELEDSENTENCE_DATA["sentence"][0]["begin"]
        assert labeledsentence.sentence[0].end == _LABELEDSENTENCE_DATA["sentence"][0]["end"]

        assert labeledsentence.spell[0].text == _LABELEDSENTENCE_DATA["spell"][0]["text"]
        assert labeledsentence.spell[0].begin == _LABELEDSENTENCE_DATA["spell"][0]["begin"]
        assert labeledsentence.spell[0].end == _LABELEDSENTENCE_DATA["spell"][0]["end"]

        assert labeledsentence.phone[0].text == _LABELEDSENTENCE_DATA["phone"][0]["text"]
        assert labeledsentence.phone[0].begin == _LABELEDSENTENCE_DATA["phone"][0]["begin"]
        assert labeledsentence.phone[0].end == _LABELEDSENTENCE_DATA["phone"][0]["end"]

    def test_dumps(self):
        begin, end = 0, 0

        sentence = [Word(text="qi1shi2", begin=begin, end=end)]
        spell = [Word(text="qi1", begin=begin, end=end)]
        phone = [Word(text="q", begin=begin, end=end)]
        attributes = {"name": "patch number"}

        labeledsentence = LabeledSentence(
            sentence=sentence, spell=spell, phone=phone, attributes=attributes
        )

        labeledsentence.dumps = _LABELEDSENTENCE_DATA


class TestLabeledKeypoints2D:
    def test_init(self):
        labeledkeypoints2d = LabeledKeypoints2D(
            [(0, 0)], category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert LabeledKeypoints2D([[0, 0]]) == LabeledKeypoints2D([(0, 0)])
        assert LabeledKeypoints2D([(0, 0, 0)]) == LabeledKeypoints2D([[0, 0, 0]])
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
        cateogry = "Animal"
        attributes = {"name": "bird"}
        instance = "a1c66a42e22c4d89"

        labeledkeypoints2d = LabeledKeypoints2D(
            [(1, 1, 2)], category=cateogry, attributes=attributes, instance=instance
        )

        assert labeledkeypoints2d.dumps() == _LABELEDKEYPOINTS2D_DATA
