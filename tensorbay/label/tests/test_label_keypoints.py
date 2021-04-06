#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from ...geometry import Keypoint2D
from .. import Keypoints2DSubcatalog, LabeledKeypoints2D
from ..supports import AttributesMixin, CategoriesMixin, IsTrackingMixin, KeypointsInfo

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


@pytest.fixture
def subcatalog_keypoings2d(
    is_tracking_data, categories_catalog_data, attributes_catalog_data, keypoints_info_data
):
    return {
        "isTracking": is_tracking_data,
        "categories": categories_catalog_data,
        "attributes": attributes_catalog_data,
        "keypoints": [keypoints_info_data],
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

    def test_eq(self):
        keypoints1 = LabeledKeypoints2D([[1, 1, 2]], category=_CATEGORY, attributes=_ATTRIBUTES)
        keypoints2 = LabeledKeypoints2D([[1, 1, 2]], category=_CATEGORY, attributes=_ATTRIBUTES)
        keypoints3 = LabeledKeypoints2D([[1, 2, 2]], category=_CATEGORY, attributes=_ATTRIBUTES)

        assert keypoints1 == keypoints2
        assert keypoints1 != keypoints3

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


class TestKeypoints2DSubcatalog:
    def test_init_subclass(self):
        keypoints2d_subcatalog = Keypoints2DSubcatalog()
        assert keypoints2d_subcatalog._supports == (
            IsTrackingMixin,
            CategoriesMixin,
            AttributesMixin,
        )

    def test_eq(self):
        content1 = {
            "isTracking": True,
            "categories": [{"name": "0"}, {"name": "1"}],
            "attributes": [{"name": "gender", "enum": ["male", "female"]}],
            "keypoints": [
                {
                    "number": 2,
                    "names": [
                        "L_shoulder",
                        "L_Elbow",
                    ],
                    "skeleton": [(0, 1)],
                }
            ],
        }
        content2 = {
            "isTracking": True,
            "categories": [{"name": "0"}, {"name": "1"}],
            "attributes": [{"name": "gender", "enum": ["male", "female"]}],
            "keypoints": [
                {
                    "number": 1,
                    "names": [
                        "L_shoulder",
                    ],
                }
            ],
        }
        keypoints2d_subcatalog1 = Keypoints2DSubcatalog.loads(content1)
        keypoints2d_subcatalog2 = Keypoints2DSubcatalog.loads(content1)
        keypoints2d_subcatalog3 = Keypoints2DSubcatalog.loads(content2)

        assert keypoints2d_subcatalog1 == keypoints2d_subcatalog2
        assert keypoints2d_subcatalog1 != keypoints2d_subcatalog3

    def test_loads(self, categories, attributes, subcatalog_keypoings2d):
        keypoints2d_subcatalog = Keypoints2DSubcatalog.loads(subcatalog_keypoings2d)

        assert keypoints2d_subcatalog.is_tracking == subcatalog_keypoings2d["isTracking"]
        assert keypoints2d_subcatalog.categories == categories
        assert keypoints2d_subcatalog.attributes == attributes

    def test_dumps(self, categories, attributes, keypoints, subcatalog_keypoings2d):
        keypoints2d_subcatalog = Keypoints2DSubcatalog()
        keypoints2d_subcatalog.is_tracking = subcatalog_keypoings2d["isTracking"]
        keypoints2d_subcatalog.categories = categories
        keypoints2d_subcatalog.attributes = attributes
        keypoints2d_subcatalog._keypoints = [keypoints]

        # isTracking will not dumps out when isTracking is false
        if not subcatalog_keypoings2d["isTracking"]:
            del subcatalog_keypoings2d["isTracking"]

        assert keypoints2d_subcatalog.dumps() == subcatalog_keypoings2d

    def test_add_keypoints(self, keypoints_info_data, keypoints, subcatalog_keypoings2d):
        keypoints2d_subcatalog = Keypoints2DSubcatalog()
        keypoints2d_subcatalog.add_keypoints(
            keypoints_info_data["number"],
            names=keypoints_info_data["names"],
            skeleton=keypoints_info_data["skeleton"],
        )

        assert keypoints2d_subcatalog.keypoints[0].number == keypoints.number
        assert keypoints2d_subcatalog.keypoints[0].names == keypoints.names
        assert keypoints2d_subcatalog.keypoints[0].skeleton == keypoints.skeleton
