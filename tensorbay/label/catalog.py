#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""This file defines class Subcatalogbase and Subcatalog classes for every LabelType."""

from typing import Any, Dict, Type, TypeVar

from ..utility import ReprMixin, ReprType, common_loads
from .label import LabelType
from .subcatalog import (
    Box2DSubcatalog,
    Box3DSubcatalog,
    ClassificationSubcatalog,
    Keypoints2DSubcatalog,
    Polygon2DSubcatalog,
    Polyline2DSubcatalog,
    SentenceSubcatalog,
)


class Catalog(ReprMixin):
    """Catalog is a mapping which contains `Subcatalog`,
    the corresponding key is the 'name' of `LabelType`.

    :param loads: A dict contains a series of Subcatalog dicts

    """

    classification: ClassificationSubcatalog
    box2d: Box2DSubcatalog
    box3d: Box3DSubcatalog
    polygon2d: Polygon2DSubcatalog
    polyline2d: Polyline2DSubcatalog
    keypoints2d: Keypoints2DSubcatalog
    sentence: SentenceSubcatalog

    _T = TypeVar("_T", bound="Catalog")
    _repr_maxlevel = 2
    _repr_type = ReprType.INSTANCE
    _repr_attrs = tuple(label_type.value for label_type in LabelType)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Load a Catalog from a dict containing the information of the Catalog.

        :param contents: A dict contains all information of the Catalog
        :return: The loaded Catalog
        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:
        for type_name, subcatalog in contents.items():
            label_type = LabelType[type_name]
            setattr(self, label_type.value, label_type.subcatalog_type.loads(subcatalog))

    def dumps(self) -> Dict[str, Any]:
        """Dump the catalog into a series of subcatalog dict

        :return: a dict contains a series of subcatalog dict with their label types as dict keys
        """
        contents: Dict[str, Any] = {}
        for label_type in LabelType:
            subcatalog = getattr(self, label_type.value, None)
            if subcatalog:
                contents[label_type.name] = subcatalog.dumps()
        return contents

    def __bool__(self) -> bool:
        for label_type in LabelType:
            if hasattr(self, label_type.value):
                return True
        return False
