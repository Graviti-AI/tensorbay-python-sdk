#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""LabeledPolygon, PolygonSubcatalog.

:class:`PolygonSubcatalog` defines the subcatalog for polygon type of labels.

:class:`LabeledPolygon` is the polygon type of label,
which is often used for CV tasks such as semantic segmentation.

"""

from typing import Any, Dict, Iterable, Optional, Type, TypeVar

from ..geometry import Polygon
from ..utility import ReprType, SubcatalogTypeRegister, TypeRegister, attr_base, common_loads
from .basic import LabelType, SubcatalogBase, _LabelBase
from .supports import AttributesMixin, CategoriesMixin, IsTrackingMixin


@SubcatalogTypeRegister(LabelType.POLYGON)
class PolygonSubcatalog(  # pylint: disable=too-many-ancestors
    SubcatalogBase, IsTrackingMixin, CategoriesMixin, AttributesMixin
):
    """This class defines the subcatalog for polygon type of labels.

    Arguments:
        is_tracking: A boolean value indicates whether the corresponding
            subcatalog contains tracking information.

    Attributes:
        description: The description of the entire polygon subcatalog.
        categories: All the possible categories in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameList`
            with the category names as keys
            and the :class:`~tensorbay.label.supports.CategoryInfo` as values.
        category_delimiter: The delimiter in category values indicating parent-child relationship.
        attributes: All the possible attributes in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameList`
            with the attribute names as keys
            and the :class:`~tensorbay.label.attribute.AttributeInfo` as values.
        is_tracking: Whether the Subcatalog contains tracking information.

    Examples:
        *Initialization Method 1:* Init from ``PolygonSubcatalog.loads()`` method.

        >>> catalog = {
        ...     "POLYGON": {
        ...         "isTracking": True,
        ...         "categories": [{"name": "0"}, {"name": "1"}],
        ...         "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        ...     }
        ... }
        >>> PolygonSubcatalog.loads(catalog["POLYGON"])
        PolygonSubcatalog(
          (is_tracking): True,
          (categories): NameList [...],
          (attributes): NameList [...]
        )

        *Initialization Method 2:* Init an empty PolygonSubcatalog and then add the attributes.

        >>> from tensorbay.utility import NameList
        >>> from tensorbay.label import CategoryInfo, AttributeInfo
        >>> categories = NameList()
        >>> categories.append(CategoryInfo("a"))
        >>> attributes = NameList()
        >>> attributes.append(AttributeInfo("gender", enum=["female", "male"]))
        >>> polygon_subcatalog = PolygonSubcatalog()
        >>> polygon_subcatalog.is_tracking = True
        >>> polygon_subcatalog.categories = categories
        >>> polygon_subcatalog.attributes = attributes
        >>> polygon_subcatalog
        PolygonSubcatalog(
          (is_tracking): True,
          (categories): NameList [...],
          (attributes): NameList [...]
        )

    """

    def __init__(self, is_tracking: bool = False) -> None:
        SubcatalogBase.__init__(self)
        IsTrackingMixin.__init__(self, is_tracking)


@TypeRegister(LabelType.POLYGON)
class LabeledPolygon(_LabelBase, Polygon):  # pylint: disable=too-many-ancestors
    """This class defines the concept of polygon label.

    :class:`LabeledPolygon` is the polygon type of label,
    which is often used for CV tasks such as semantic segmentation.

    Arguments:
        points: A list of 2D points representing the vertexes of the polygon.
        category: The category of the label.
        attributes: The attributs of the label.
        instance: The instance id of the label.

    Attributes:
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    Examples:
        >>> LabeledPolygon(
        ...     [(1, 2), (2, 3), (1, 3)],
        ...     category = "example",
        ...     attributes = {"key": "value"},
        ...     instance = "123",
        ... )
        LabeledPolygon [
          Vector2D(1, 2),
          Vector2D(2, 3),
          Vector2D(1, 3)
        ](
          (category): 'example',
          (attributes): {...},
          (instance): '123'
        )

    """

    _T = TypeVar("_T", bound="LabeledPolygon")

    _repr_type = ReprType.SEQUENCE
    _repr_attrs = _LabelBase._repr_attrs
    _attrs_base: Polygon = attr_base(key="polygon")

    def __init__(
        self,
        points: Optional[Iterable[Iterable[float]]] = None,
        *,
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        instance: Optional[str] = None,
    ):
        Polygon.__init__(self, points)  # type: ignore[arg-type]
        _LabelBase.__init__(self, category, attributes, instance)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:  # type: ignore[override]
        """Loads a LabeledPolygon from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the polygon label.

        Returns:
            The loaded :class:`LabeledPolygon` object.

        Examples:
            >>> contents = {
            ...     "polygon": [
            ...         {"x": 1, "y": 2},
            ...         {"x": 2, "y": 3},
            ...         {"x": 1, "y": 3},
            ...     ],
            ...     "category": "example",
            ...     "attributes": {"key": "value"},
            ...     "instance": "12345",
            ... }
            >>> LabeledPolygon.loads(contents)
            LabeledPolygon [
              Vector2D(1, 2),
              Vector2D(2, 3),
              Vector2D(1, 3)
            ](
              (category): 'example',
              (attributes): {...},
              (instance): '12345'
            )

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:  # type: ignore[override]
        """Dumps the current polygon label into a dict.

        Returns:
            A dict containing all the information of the polygon label.

        Examples:
            >>> labeledpolygon = LabeledPolygon(
            ...     [(1, 2), (2, 3), (1, 3)],
            ...     category = "example",
            ...     attributes = {"key": "value"},
            ...     instance = "123",
            ... )
            >>> labeledpolygon.dumps()
            {
                'category': 'example',
                'attributes': {'key': 'value'},
                'instance': '123',
                'polygon': [{'x': 1, 'y': 2}, {'x': 2, 'y': 3}, {'x': 1, 'y': 3}],
            }

        """
        return self._dumps()
