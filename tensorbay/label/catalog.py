#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""The implementation of the TensorBay catalog."""

from functools import partial
from typing import Any, Dict, Iterator, Type, TypeVar

from tensorbay.label.label_box import Box2DSubcatalog, Box3DSubcatalog
from tensorbay.label.label_classification import ClassificationSubcatalog
from tensorbay.label.label_keypoints import Keypoints2DSubcatalog
from tensorbay.label.label_mask import (
    InstanceMaskSubcatalog,
    PanopticMaskSubcatalog,
    SemanticMaskSubcatalog,
)
from tensorbay.label.label_polygon import MultiPolygonSubcatalog, PolygonSubcatalog, RLESubcatalog
from tensorbay.label.label_polyline import MultiPolyline2DSubcatalog, Polyline2DSubcatalog
from tensorbay.label.label_sentence import SentenceSubcatalog
from tensorbay.utility import AttrsMixin, ReprMixin, ReprType, attr, common_loads, upper

_ERROR_MESSAGE = "The '{attr_name}' subcatalog is not provided in this dataset"
_attr = partial(attr, is_dynamic=True, key=upper, error_message=_ERROR_MESSAGE)


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
        >>> from tensorbay.utility import NameList
        >>> from tensorbay.label import ClassificationSubcatalog, CategoryInfo
        >>> classification_subcatalog = ClassificationSubcatalog()
        >>> categories = NameList()
        >>> categories.append(CategoryInfo("example"))
        >>> classification_subcatalog.categories = categories
        >>> catalog = Catalog()
        >>> catalog.classification = classification_subcatalog
        >>> catalog
        Catalog(
          (classification): ClassificationSubcatalog(
            (categories): NameList [...]
          )
        )

    """

    _T = TypeVar("_T", bound="Catalog")

    _repr_type = ReprType.INSTANCE
    _repr_maxlevel = 2

    classification: ClassificationSubcatalog = _attr()
    box2d: Box2DSubcatalog = _attr()
    box3d: Box3DSubcatalog = _attr()
    polygon: PolygonSubcatalog = _attr()
    polyline2d: Polyline2DSubcatalog = _attr()
    multi_polyline2d: MultiPolyline2DSubcatalog = _attr()
    keypoints2d: Keypoints2DSubcatalog = _attr()
    multi_polygon: MultiPolygonSubcatalog = _attr()
    rle: RLESubcatalog = _attr()
    sentence: SentenceSubcatalog = _attr()
    semantic_mask: SemanticMaskSubcatalog = _attr()
    instance_mask: InstanceMaskSubcatalog = _attr()
    panoptic_mask: PanopticMaskSubcatalog = _attr()

    def __bool__(self) -> bool:
        return any(hasattr(self, key) for key in self._attrs_fields)

    @property
    def _repr_attrs(self) -> Iterator[str]:  # type: ignore[override]
        yield from self._attrs_fields

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
                (categories): NameList [...]
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
