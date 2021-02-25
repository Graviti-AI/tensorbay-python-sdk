#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Label related classes."""

from .attributes import AttributeInfo, Items
from .catalog import Catalog
from .label import (
    Classification,
    Label,
    LabeledBox2D,
    LabeledBox3D,
    LabeledKeypoints2D,
    LabeledPolygon2D,
    LabeledPolyline2D,
    LabeledSentence,
    LabelType,
    Word,
)
from .subcatalog import (
    Box2DSubcatalog,
    Box3DSubcatalog,
    ClassificationSubcatalog,
    Keypoints2DSubcatalog,
    Polygon2DSubcatalog,
    Polyline2DSubcatalog,
    SentenceSubcatalog,
    Subcatalogs,
)
from .supports import CategoryInfo, KeypointsInfo, VisibleType

__all__ = [
    "AttributeInfo",
    "Items",
    "SentenceSubcatalog",
    "CategoryInfo",
    "Classification",
    "KeypointsInfo",
    "Keypoints2DSubcatalog",
    "ClassificationSubcatalog",
    "Box2DSubcatalog",
    "Box3DSubcatalog",
    "Polygon2DSubcatalog",
    "Polyline2DSubcatalog",
    "Subcatalogs",
    "Label",
    "Catalog",
    "LabelType",
    "LabeledBox2D",
    "LabeledBox3D",
    "LabeledKeypoints2D",
    "LabeledPolygon2D",
    "LabeledPolyline2D",
    "LabeledSentence",
    "VisibleType",
    "Word",
]
