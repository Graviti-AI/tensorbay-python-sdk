#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Label related classes."""

from .attributes import AttributeInfo, Items
from .catalog import Catalog
from .label import Label
from .label_box import Box2DSubcatalog, Box3DSubcatalog, LabeledBox2D, LabeledBox3D
from .label_classification import Classification, ClassificationSubcatalog
from .label_keypoints import Keypoints2DSubcatalog, LabeledKeypoints2D
from .label_mask import (
    InstanceMask,
    InstanceMaskSubcatalog,
    PanopticMask,
    PanopticMaskSubcatalog,
    SemanticMask,
    SemanticMaskSubcatalog,
)
from .label_polygon import (
    LabeledMultiPolygon,
    LabeledPolygon,
    LabeledRLE,
    MultiPolygonSubcatalog,
    PolygonSubcatalog,
    RLESubcatalog,
)
from .label_polyline import (
    LabeledMultiPolyline2D,
    LabeledPolyline2D,
    MultiPolyline2DSubcatalog,
    Polyline2DSubcatalog,
)
from .label_sentence import LabeledSentence, SentenceSubcatalog, Word
from .supports import CategoryInfo, KeypointsInfo, MaskCategoryInfo

__all__ = [
    "AttributeInfo",
    "Box2DSubcatalog",
    "Box3DSubcatalog",
    "Catalog",
    "CategoryInfo",
    "Classification",
    "ClassificationSubcatalog",
    "InstanceMask",
    "InstanceMaskSubcatalog",
    "Items",
    "Keypoints2DSubcatalog",
    "KeypointsInfo",
    "Label",
    "LabeledBox2D",
    "LabeledBox3D",
    "LabeledKeypoints2D",
    "LabeledMultiPolygon",
    "LabeledMultiPolyline2D",
    "LabeledPolygon",
    "LabeledPolyline2D",
    "LabeledRLE",
    "LabeledSentence",
    "MaskCategoryInfo",
    "MultiPolygonSubcatalog",
    "MultiPolyline2DSubcatalog",
    "PanopticMask",
    "PanopticMaskSubcatalog",
    "PolygonSubcatalog",
    "Polyline2DSubcatalog",
    "RLESubcatalog",
    "SemanticMask",
    "SemanticMaskSubcatalog",
    "SentenceSubcatalog",
    "Word",
]
