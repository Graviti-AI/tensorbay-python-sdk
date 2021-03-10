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

_CATEGORY = "test"
_ATTRIBUTES = {"key": "value"}
_INSTANCE = "12345"

_TEXT = "Hello, World"
_BEGIN = 1
_END = 1

_CLASSIFICATION_DATA = {"category": "test", "attributes": {"key": "value"}}

_LABELEDBOX2D_DATA = {
    "box2d": {"xmin": 1, "ymin": 2, "xmax": 5, "ymax": 8},
    "category": "test",
    "attributes": {"key": "value"},
    "instance": "12345",
}

_LABELEDBOX3D_DATA = {
    "box3d": {
        "translation": {"x": 1, "y": 2, "z": 3},
        "rotation": {"w": 1, "x": 2, "y": 3, "z": 4},
        "size": {"x": 1, "y": 2, "z": 3},
    },
    "category": "test",
    "attributes": {"key": "value"},
    "instance": "12345",
}

_LABELEDPOLYGON2D_DATA = {
    "polygon2d": [
        {"x": 1, "y": 2},
    ],
    "category": "test",
    "attributes": {"key": "value"},
    "instance": "12345",
}

_LABELEDPOLYLINE2D_DATA = {
    "polyline2d": [{"x": 1, "y": 2}],
    "category": "test",
    "attributes": {"key": "value"},
    "instance": "12345",
}

_WORD_DATA = {"text": "Hello, World", "begin": 1, "end": 1}

_LABELEDSENTENCE_DATA = {
    "sentence": [{"text": "qi1shi2", "begin": 1, "end": 1}],
    "spell": [{"text": "qi1", "begin": 1, "end": 1}],
    "phone": [{"text": "q", "begin": 1, "end": 1}],
    "attributes": {"key": "value"},
}

_LABELEDKEYPOINTS2D_DATA = {
    "keypoints2d": [
        {"x": 1, "y": 1, "v": 2},
    ],
    "category": "test",
    "attributes": {"key": "value"},
    "instance": "12345",
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
        classification = Classification(category=_CATEGORY, attributes=_ATTRIBUTES)

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
        labeledbox2d = LabeledBox2D(
            category=_CATEGORY,
            attributes=_ATTRIBUTES,
            instance=_INSTANCE,
            x=1,
            y=2,
            width=4,
            height=6,
        )

        assert labeledbox2d.dumps() == _LABELEDBOX2D_DATA


class TestLabeledBox3D:
    def test_init(self):
        translation = Vector3D(1, 2, 3)
        rotation = Quaternion(1, 2, 3, 4)
        size = Vector3D(1, 2, 3)
        transform = Transform3D(translation=translation, rotation=rotation)

        labeledbox3d = LabeledBox3D(
            transform, size=size, category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert labeledbox3d.translation == translation
        assert labeledbox3d.rotation == rotation
        assert labeledbox3d.size == size
        assert labeledbox3d.category == _CATEGORY
        assert labeledbox3d.attributes == _ATTRIBUTES
        assert labeledbox3d.instance == _INSTANCE

    def test_rmul(self):
        translation = [1, 2, 3]
        rotation = Quaternion(0, 1, 0, 0)
        transform = Transform3D(translation=translation, rotation=rotation)

        labeledbox3d = LabeledBox3D(
            transform, category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert labeledbox3d.__rmul__(transform).category == _CATEGORY
        assert labeledbox3d.__rmul__(transform).attributes == _ATTRIBUTES
        assert labeledbox3d.__rmul__(transform).instance == _INSTANCE

        assert labeledbox3d.__rmul__(1) == NotImplemented

    def test_loads(self):
        labeledbox3d = LabeledBox3D.loads(_LABELEDBOX3D_DATA)

        assert labeledbox3d.category == _LABELEDBOX3D_DATA["category"]
        assert labeledbox3d.attributes == _LABELEDBOX3D_DATA["attributes"]
        assert labeledbox3d.instance == _LABELEDBOX3D_DATA["instance"]

        assert labeledbox3d.translation == Vector3D(1, 2, 3)
        assert labeledbox3d.rotation == Quaternion(1, 2, 3, 4)
        assert labeledbox3d.size == Vector3D(1, 2, 3)

    def test_dumps(self):
        translation = [1, 2, 3]
        rotation = Quaternion(1, 2, 3, 4)
        size = [1, 2, 3]
        transform = Transform3D(translation=translation, rotation=rotation)

        labeledbox3d = LabeledBox3D(
            transform, size=size, category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert labeledbox3d.dumps() == _LABELEDBOX3D_DATA


class TestLabeledPolygon2D:
    def test_init(self):
        labeledpolygon2d = LabeledPolygon2D(
            [(1, 2)], category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert labeledpolygon2d[0] == Vector2D(1, 2)
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
        labeledpolygon2d = LabeledPolygon2D(
            [(1, 2)], category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert labeledpolygon2d.dumps() == _LABELEDPOLYGON2D_DATA


class TestLabeledPolyline2D:
    def test_init(self):
        labeledpolyline2d = LabeledPolyline2D(
            [(1, 2)], category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert labeledpolyline2d[0] == Vector2D(1, 2)
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
        labeledpolygonline2d = LabeledPolyline2D(
            [(1, 2)], category=_CATEGORY, attributes=_ATTRIBUTES, instance=_INSTANCE
        )

        assert labeledpolygonline2d.dumps() == _LABELEDPOLYLINE2D_DATA


class TestWord:
    def test_init(self):
        word = Word(text=_TEXT, begin=_BEGIN, end=_END)

        assert word.text == _TEXT
        assert word.begin == _BEGIN
        assert word.end == _END

    def test_loads(self):
        word = Word.loads(_WORD_DATA)

        assert word.text == _TEXT
        assert word.begin == _BEGIN
        assert word.end == _END

    def test_dumps(self):
        word = Word(text=_TEXT, begin=_BEGIN, end=_END)

        assert word.dumps() == _WORD_DATA


class TestLabeledSentence:
    def test_init(self):
        sentence = [Word(text="qi1shi2", begin=_BEGIN, end=_END)]
        spell = [Word(text="qi1", begin=_BEGIN, end=_END)]
        phone = [Word(text="q", begin=_BEGIN, end=_END)]

        labeledsentence = LabeledSentence(
            sentence=sentence, spell=spell, phone=phone, attributes=_ATTRIBUTES
        )

        assert labeledsentence.sentence == list(sentence)
        assert labeledsentence.spell == list(spell)
        assert labeledsentence.phone == list(phone)

    def test_load_word(self):
        sentence = LabeledSentence._load_word(_LABELEDSENTENCE_DATA["sentence"])
        spell = LabeledSentence._load_word(_LABELEDSENTENCE_DATA["spell"])
        phone = LabeledSentence._load_word(_LABELEDSENTENCE_DATA["phone"])

        assert sentence[0].text == "qi1shi2"
        assert sentence[0].begin == _BEGIN
        assert sentence[0].end == _END

        assert spell[0].text == "qi1"
        assert spell[0].begin == _BEGIN
        assert spell[0].end == _END

        assert phone[0].text == "q"
        assert phone[0].begin == _BEGIN
        assert phone[0].end == _END

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
        sentence = [Word(text="qi1shi2", begin=_BEGIN, end=_END)]
        spell = [Word(text="qi1", begin=_BEGIN, end=_END)]
        phone = [Word(text="q", begin=_BEGIN, end=_END)]

        labeledsentence = LabeledSentence(
            sentence=sentence, spell=spell, phone=phone, attributes=_ATTRIBUTES
        )

        labeledsentence.dumps = _LABELEDSENTENCE_DATA


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
