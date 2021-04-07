#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#


import pytest

from ...utility import NameOrderedDict
from .. import (
    Box2DSubcatalog,
    Box3DSubcatalog,
    Catalog,
    ClassificationSubcatalog,
    Keypoints2DSubcatalog,
    Polygon2DSubcatalog,
    Polyline2DSubcatalog,
    SentenceSubcatalog,
)
from ..supports import CategoryInfo, KeypointsInfo

_CATALOG_DICT = {
    "classification": ClassificationSubcatalog,
    "box2d": Box2DSubcatalog,
    "box3d": Box3DSubcatalog,
    "polygon2d": Polygon2DSubcatalog,
    "polyline2d": Polyline2DSubcatalog,
    "keypoints2d": Keypoints2DSubcatalog,
    "sentence": SentenceSubcatalog,
}


@pytest.fixture
def catalog_contents(categories_catalog_data, keypoints_info_data):
    return {
        "BOX2D": {},
        "BOX3D": {},
        "POLYGON2D": {},
        "POLYLINE2D": {},
        "SENTENCE": {},
        "CLASSIFICATION": {"categories": categories_catalog_data},
        "KEYPOINTS2D": {"keypoints": [keypoints_info_data]},
    }


class TestCatalog:
    def test_bool(self):
        catalog = Catalog()
        assert catalog.__bool__() == False

        catalog.box2d = Box2DSubcatalog()
        assert catalog.__bool__() == True

    def test_eq(self):
        catalog1 = Catalog()
        catalog1.box2d = Box2DSubcatalog()
        catalog2 = Catalog()
        catalog2.box2d = Box2DSubcatalog()
        catalog3 = Catalog()
        catalog3.box3d = Box3DSubcatalog()

        assert catalog1 == catalog2
        assert catalog1 != catalog3

    def test_loads(self, catalog_contents):
        catalog = Catalog.loads(catalog_contents)
        for key, value in _CATALOG_DICT.items():
            assert isinstance(getattr(catalog, key), value)

    def test_dumps(self, categories, keypoints, catalog_contents):
        catalog = Catalog()
        catalog.box2d = Box2DSubcatalog()
        catalog.box3d = Box3DSubcatalog()
        catalog.polygon2d = Polygon2DSubcatalog()
        catalog.polyline2d = Polyline2DSubcatalog()
        catalog.sentence = SentenceSubcatalog()

        classificationsubcatalog = ClassificationSubcatalog()
        classificationsubcatalog.categories = categories
        catalog.classification = classificationsubcatalog

        keypoints2dsubcatalog = Keypoints2DSubcatalog()
        keypoints2dsubcatalog._keypoints = [keypoints]
        catalog.keypoints2d = keypoints2dsubcatalog

        assert catalog.dumps() == catalog_contents
