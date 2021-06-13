#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""LabeledPolygon2D, Polygon2DSubcatalog.

:class:`Polygon2DSubcatalog` defines the subcatalog for 2D polygon type of labels.

:class:`LabeledPolygon2D` is the 2D polygon type of label,
which is often used for CV tasks such as semantic segmentation.

"""

from typing import Any, Dict, Iterable, Optional, Type, TypeVar

from ..geometry import Polygon2D
from ..utility import ReprType, SubcatalogTypeRegister, TypeRegister, attr_base, common_loads
from .basic import LabelType, SubcatalogBase, _LabelBase
from .supports import AttributesMixin, CategoriesMixin, IsTrackingMixin


@SubcatalogTypeRegister(LabelType.POLYGON2D)
class Polygon2DSubcatalog(  # pylint: disable=too-many-ancestors
    SubcatalogBase, IsTrackingMixin, CategoriesMixin, AttributesMixin
):
    """This class defines the subcatalog for 2D polygon type of labels.

    Arguments:
        is_tracking: A boolean value indicates whether the corresponding
            subcatalog contains tracking information.

    Attributes:
        description: The description of the entire 2D polygon subcatalog.
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
        *Initialization Method 1:* Init from ``Polygon2DSubcatalog.loads()`` method.

        >>> catalog = {
        ...     "POLYGON2D": {
        ...         "isTracking": True,
        ...         "categories": [{"name": "0"}, {"name": "1"}],
        ...         "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        ...     }
        ... }
        >>> Polygon2DSubcatalog.loads(catalog["POLYGON2D"])
        Polygon2DSubcatalog(
          (is_tracking): True,
          (categories): NameList [...],
          (attributes): NameList [...]
        )

        *Initialization Method 2:* Init an empty Polygon2DSubcatalog and then add the attributes.

        >>> from tensorbay.utility import NameList
        >>> from tensorbay.label import CategoryInfo, AttributeInfo
        >>> categories = NameList()
        >>> categories.append(CategoryInfo("a"))
        >>> attributes = NameList()
        >>> attributes.append(AttributeInfo("gender", enum=["female", "male"]))
        >>> polygon2d_subcatalog = Polygon2DSubcatalog()
        >>> polygon2d_subcatalog.is_tracking = True
        >>> polygon2d_subcatalog.categories = categories
        >>> polygon2d_subcatalog.attributes = attributes
        >>> polygon2d_subcatalog
        Polygon2DSubcatalog(
          (is_tracking): True,
          (categories): NameList [...],
          (attributes): NameList [...]
        )

    """

    def __init__(self, is_tracking: bool = False) -> None:
        SubcatalogBase.__init__(self)
        IsTrackingMixin.__init__(self, is_tracking)


@TypeRegister(LabelType.POLYGON2D)
class LabeledPolygon2D(_LabelBase, Polygon2D):  # pylint: disable=too-many-ancestors
    """This class defines the concept of polygon2D label.

    :class:`LabeledPolygon2D` is the 2D polygon type of label,
    which is often used for CV tasks such as semantic segmentation.

    Arguments:
        points: A list of 2D points representing the vertexes of the 2D polygon.
        category: The category of the label.
        attributes: The attributs of the label.
        instance: The instance id of the label.

    Attributes:
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    Examples:
        >>> LabeledPolygon2D(
        ...     [(1, 2), (2, 3), (1, 3)],
        ...     category = "example",
        ...     attributes = {"key": "value"},
        ...     instance = "123",
        ... )
        LabeledPolygon2D [
          Vector2D(1, 2),
          Vector2D(2, 3),
          Vector2D(1, 3)
        ](
          (category): 'example',
          (attributes): {...},
          (instance): '123'
        )

    """

    _T = TypeVar("_T", bound="LabeledPolygon2D")

    _repr_type = ReprType.SEQUENCE
    _repr_attrs = _LabelBase._repr_attrs
    _attrs_base: Polygon2D = attr_base(key="polygon2d")

    def __init__(
        self,
        points: Optional[Iterable[Iterable[float]]] = None,
        *,
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        instance: Optional[str] = None,
    ):
        Polygon2D.__init__(self, points)  # type: ignore[arg-type]
        _LabelBase.__init__(self, category, attributes, instance)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:  # type: ignore[override]
        """Loads a LabeledPolygon2D from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the 2D polygon label.

        Returns:
            The loaded :class:`LabeledPolygon2D` object.

        Examples:
            >>> contents = {
            ...     "polygon2d": [
            ...         {"x": 1, "y": 2},
            ...         {"x": 2, "y": 3},
            ...         {"x": 1, "y": 3},
            ...     ],
            ...     "category": "example",
            ...     "attributes": {"key": "value"},
            ...     "instance": "12345",
            ... }
            >>> LabeledPolygon2D.loads(contents)
            LabeledPolygon2D [
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
        """Dumps the current 2D polygon label into a dict.

        Returns:
            A dict containing all the information of the 2D polygon label.

        Examples:
            >>> labeledpolygon2d = LabeledPolygon2D(
            ...     [(1, 2), (2, 3), (1, 3)],
            ...     category = "example",
            ...     attributes = {"key": "value"},
            ...     instance = "123",
            ... )
            >>> labeledpolygon2d.dumps()
            {
                'category': 'example',
                'attributes': {'key': 'value'},
                'instance': '123',
                'polygon2d': [{'x': 1, 'y': 2}, {'x': 2, 'y': 3}, {'x': 1, 'y': 3}],
            }

        """
        return self._dumps()
