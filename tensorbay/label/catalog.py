#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Catalog.

:class:`Catalog` is used to describe the types of labels
contained in a :class:`~tensorbay.dataset.dataset.DatasetBase` and
all the optional values of the label contents.

"""

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
    """This class defines the concept of catalog.

    :class:`Catalog` is used to describe the types of labels
    contained in a :class:`~tensorbay.dataset.dataset.DatasetBase`
    and all the optional values of the label contents.

    A :class:`Catalog` contains one or several :class:`~tensorbay.label.subcatalog.SubcatalogBase`,
    corresponding to different types of labels.
    Each of the :class:`~tensorbay.label.subcatalog.SubcatalogBase`
    contains the features, fields and the specific definitions of the labels.

    """

    _T = TypeVar("_T", bound="Catalog")

    _repr_type = ReprType.INSTANCE
    _repr_attrs = tuple(label_type.value for label_type in LabelType)
    _repr_maxlevel = 2

    classification: ClassificationSubcatalog
    box2d: Box2DSubcatalog
    box3d: Box3DSubcatalog
    polygon2d: Polygon2DSubcatalog
    polyline2d: Polyline2DSubcatalog
    keypoints2d: Keypoints2DSubcatalog
    sentence: SentenceSubcatalog

    def __bool__(self) -> bool:
        for label_type in LabelType:
            if hasattr(self, label_type.value):
                return True
        return False

    def _loads(self, contents: Dict[str, Any]) -> None:
        for type_name, subcatalog in contents.items():
            label_type = LabelType[type_name]
            setattr(self, label_type.value, label_type.subcatalog_type.loads(subcatalog))

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Load a Catalog from a dict containing the catalog information.

        Arguments:
            contents: A dict containing all the information of the catalog.

        Returns:
            The loaded :class:`Catalog` object.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the catalog into a dict containing the information of all the subcatalog.

        Returns:
            A dict containing all the subcatalog information with their label types as keys.

        """
        contents: Dict[str, Any] = {}
        for label_type in LabelType:
            subcatalog = getattr(self, label_type.value, None)
            if subcatalog:
                contents[label_type.name] = subcatalog.dumps()
        return contents
