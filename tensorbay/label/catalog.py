#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Catalog.

:class:`Catalog` is used to describe the types of labels
contained in a :class:`~tensorbay.dataset.dataset.DatasetBase` and
all the optional values of the label contents.

A :class:`Catalog` contains one or several :class:`~tensorbay.label.basic.SubcatalogBase`,
corresponding to different types of labels.

.. table:: subcatalog classes
   :widths: auto

   ==================================   ==================================================
   subcatalog classes                   explaination
   ==================================   ==================================================
   :class:`.ClassificationSubcatalog`   subcatalog for classification type of label
   :class:`.Box2DSubcatalog`            subcatalog for 2D bounding box type of label
   :class:`.Box3DSubcatalog`            subcatalog for 3D bounding box type of label
   :class:`.Keypoints2DSubcatalog`      subcatalog for 2D polygon type of label
   :class:`.Polygon2DSubcatalog`        subcatalog for 2D polyline type of label
   :class:`.Polyline2DSubcatalog`       subcatalog for 2D keypoints type of label
   :class:`.SentenceSubcatalog`         subcatalog for transcripted sentence type of label
   ==================================   ==================================================

"""

from typing import Any, Dict, Type, TypeVar, Union

from ..label import LabelType
from ..utility import AttrsMixin, ReprMixin, ReprType, attr, common_loads, upper
from .label_box import Box2DSubcatalog, Box3DSubcatalog
from .label_classification import ClassificationSubcatalog
from .label_keypoints import Keypoints2DSubcatalog
from .label_polygon import Polygon2DSubcatalog
from .label_polyline import Polyline2DSubcatalog
from .label_sentence import SentenceSubcatalog

Subcatalogs = Union[
    ClassificationSubcatalog,
    Box2DSubcatalog,
    Box3DSubcatalog,
    Polygon2DSubcatalog,
    Polyline2DSubcatalog,
    Keypoints2DSubcatalog,
    SentenceSubcatalog,
]


class Catalog(ReprMixin, AttrsMixin):
    """This class defines the concept of catalog.

    :class:`Catalog` is used to describe the types of labels
    contained in a :class:`~tensorbay.dataset.dataset.DatasetBase`
    and all the optional values of the label contents.

    A :class:`Catalog` contains one or several :class:`~tensorbay.label.basic.SubcatalogBase`,
    corresponding to different types of labels.
    Each of the :class:`~tensorbay.label.basic.SubcatalogBase`
    contains the features, fields and the specific definitions of the labels.

    Examples:
        >>> from tensorbay.utility import NamedList
        >>> from tensorbay.label import ClassificationSubcatalog, CategoryInfo
        >>> classification_subcatalog = ClassificationSubcatalog()
        >>> categories = NamedList()
        >>> categories.append(CategoryInfo("example"))
        >>> classification_subcatalog.categories = categories
        >>> catalog = Catalog()
        >>> catalog.classification = classification_subcatalog
        >>> catalog
        Catalog(
          (classification): ClassificationSubcatalog(
            (categories): NamedList [...]
          )
        )

    """

    _T = TypeVar("_T", bound="Catalog")

    _repr_type = ReprType.INSTANCE
    _repr_attrs = tuple(label_type.value for label_type in LabelType)
    _repr_maxlevel = 2

    classification: ClassificationSubcatalog = attr(is_dynamic=True, key=upper)
    box2d: Box2DSubcatalog = attr(is_dynamic=True, key=upper)
    box3d: Box3DSubcatalog = attr(is_dynamic=True, key=upper)
    polygon2d: Polygon2DSubcatalog = attr(is_dynamic=True, key=upper)
    polyline2d: Polyline2DSubcatalog = attr(is_dynamic=True, key=upper)
    keypoints2d: Keypoints2DSubcatalog = attr(is_dynamic=True, key=upper)
    sentence: SentenceSubcatalog = attr(is_dynamic=True, key=upper)

    def __bool__(self) -> bool:
        for label_type in LabelType:
            if hasattr(self, label_type.value):
                return True
        return False

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Load a Catalog from a dict containing the catalog information.

        Arguments:
            contents: A dict containing all the information of the catalog.

        Returns:
            The loaded :class:`Catalog` object.

        Examples:
            >>> contents = {
            ...     "CLASSIFICATION": {
            ...         "categories": [
            ...             {
            ...                 "name": "example",
            ...             }
            ...         ]
            ...     },
            ...     "KEYPOINTS2D": {
            ...         "keypoints": [
            ...             {
            ...                 "number": 5,
            ...             }
            ...         ]
            ...     },
            ... }
            >>> Catalog.loads(contents)
            Catalog(
              (classification): ClassificationSubcatalog(
                (categories): NamedList [...]
              ),
              (keypoints2d): Keypoints2DSubcatalog(
                (is_tracking): False,
                (keypoints): [...]
              )
            )

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the catalog into a dict containing the information of all the subcatalog.

        Returns:
            A dict containing all the subcatalog information with their label types as keys.

        Examples:
            >>> # catalog is the instance initialized above.
            >>> catalog.dumps()
            {'CLASSIFICATION': {'categories': [{'name': 'example'}]}}

        """
        return self._dumps()
