#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""LabeledPolyline2D, Polyline2DSubcatalog.

:class:`Polyline2DSubcatalog` defines the subcatalog for 2D polyline type of labels.

:class:`LabeledPolyline2D` is the 2D polyline type of label,
which is often used for CV tasks such as lane detection.

"""

from typing import Any, Dict, Iterable, Optional, Type, TypeVar

from ..geometry import MultiPolyline2D, Polyline2D
from ..utility import ReprType, attr_base, common_loads
from .basic import SubcatalogBase, _LabelBase
from .supports import AttributesMixin, CategoriesMixin, IsTrackingMixin


class Polyline2DSubcatalog(SubcatalogBase, IsTrackingMixin, CategoriesMixin, AttributesMixin):
    """This class defines the subcatalog for 2D polyline type of labels.

    Arguments:
        is_tracking: A boolean value indicates whether the corresponding
            subcatalog contains tracking information.

    Attributes:
        description: The description of the entire 2D polyline subcatalog.
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
        *Initialization Method 1:* Init from ``Polyline2DSubcatalog.loads()`` method.

        >>> catalog = {
        ...     "POLYLINE2D": {
        ...         "isTracking": True,
        ...         "categories": [{"name": "0"}, {"name": "1"}],
        ...         "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        ...     }
        ... }
        >>> Polyline2DSubcatalog.loads(catalog["POLYLINE2D"])
        Polyline2DSubcatalog(
          (is_tracking): True,
          (categories): NameList [...],
          (attributes): NameList [...]
        )

        *Initialization Method 2:* Init an empty Polyline2DSubcatalog and then add the attributes.

        >>> from tensorbay.label import CategoryInfo, AttributeInfo
        >>> from tensorbay.utility import NameList
        >>> categories = NameList()
        >>> categories.append(CategoryInfo("a"))
        >>> attributes = NameList()
        >>> attributes.append(AttributeInfo("gender", enum=["female", "male"]))
        >>> polyline2d_subcatalog = Polyline2DSubcatalog()
        >>> polyline2d_subcatalog.is_tracking = True
        >>> polyline2d_subcatalog.categories = categories
        >>> polyline2d_subcatalog.attributes = attributes
        >>> polyline2d_subcatalog
        Polyline2DSubcatalog(
          (is_tracking): True,
          (categories): NameList [...],
          (attributes): NameList [...]
        )

    """

    def __init__(self, is_tracking: bool = False) -> None:
        SubcatalogBase.__init__(self)
        IsTrackingMixin.__init__(self, is_tracking)


class LabeledPolyline2D(_LabelBase, Polyline2D):  # pylint: disable=too-many-ancestors
    """This class defines the concept of polyline2D label.

    :class:`LabeledPolyline2D` is the 2D polyline type of label,
    which is often used for CV tasks such as lane detection.

    Arguments:
        points: A list of 2D points representing the vertexes of the 2D polyline.
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    Attributes:
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    Examples:
        >>> LabeledPolyline2D(
        ...     [(1, 2), (2, 4), (2, 1)],
        ...     category="example",
        ...     attributes={"key": "value"},
        ...     instance="123",
        ... )
        LabeledPolyline2D [
          Vector2D(1, 2),
          Vector2D(2, 4),
          Vector2D(2, 1)
        ](
          (category): 'example',
          (attributes): {...},
          (instance): '123'
        )

    """

    _T = TypeVar("_T", bound="LabeledPolyline2D")

    _repr_type = ReprType.SEQUENCE
    _repr_attrs = _LabelBase._repr_attrs
    _attrs_base: Polyline2D = attr_base(key="polyline2d")

    def __init__(
        self,
        points: Optional[Iterable[Iterable[float]]] = None,
        *,
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        instance: Optional[str] = None,
    ):
        Polyline2D.__init__(self, points)  # type: ignore[arg-type]
        _LabelBase.__init__(self, category, attributes, instance)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:  # type: ignore[override]
        """Loads a LabeledPolyline2D from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the 2D polyline label.

        Returns:
            The loaded :class:`LabeledPolyline2D` object.

        Examples:
            >>> contents = {
            ...     "polyline2d": [{'x': 1, 'y': 2}, {'x': 2, 'y': 4}, {'x': 2, 'y': 1}],
            ...     "category": "example",
            ...     "attributes": {"key": "value"},
            ...     "instance": "12345",
            ... }
            >>> LabeledPolyline2D.loads(contents)
            LabeledPolyline2D [
              Vector2D(1, 2),
              Vector2D(2, 4),
              Vector2D(2, 1)
            ](
              (category): 'example',
              (attributes): {...},
              (instance): '12345'
            )

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:  # type: ignore[override]
        """Dumps the current 2D polyline label into a dict.

        Returns:
            A dict containing all the information of the 2D polyline label.

        Examples:
            >>> labeledpolyline2d = LabeledPolyline2D(
            ...     [(1, 2), (2, 4), (2, 1)],
            ...     category="example",
            ...     attributes={"key": "value"},
            ...     instance="123",
            ... )
            >>> labeledpolyline2d.dumps()
            {
                'category': 'example',
                'attributes': {'key': 'value'},
                'instance': '123',
                'polyline2d': [{'x': 1, 'y': 2}, {'x': 2, 'y': 4}, {'x': 2, 'y': 1}],
            }

        """
        return self._dumps()


class MultiPolyline2DSubcatalog(SubcatalogBase, IsTrackingMixin, CategoriesMixin, AttributesMixin):
    """This class defines the subcatalog for 2D multiple polyline type of labels.

    Arguments:
        is_tracking: A boolean value indicates whether the corresponding
            subcatalog contains tracking information.

    Attributes:
        description: The description of the entire 2D multiple polyline subcatalog.
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
        *Initialization Method 1:* Init from ``MultiPolyline2DSubcatalog.loads()`` method.

        >>> catalog = {
        ...     "MULTI_POLYLINE2D": {
        ...         "isTracking": True,
        ...         "categories": [{"name": "0"}, {"name": "1"}],
        ...         "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        ...     }
        ... }
        >>> MultiPolyline2DSubcatalog.loads(catalog["MULTI_POLYLINE2D"])
        MultiPolyline2DSubcatalog(
          (is_tracking): True,
          (categories): NameList [...],
          (attributes): NameList [...]
        )

        *Initialization Method 2:* Init an empty MultiPolyline2DSubcatalog
        and then add the attributes.

        >>> from tensorbay.label import CategoryInfo, AttributeInfo
        >>> multi_polyline2d_subcatalog = MultiPolyline2DSubcatalog()
        >>> multi_polyline2d_subcatalog.is_tracking = True
        >>> multi_polyline2d_subcatalog.add_category(CategoryInfo("a"))
        >>> multi_polyline2d_subcatalog.add_attribute(
            AttributeInfo("gender", enum=["female", "male"]))
        >>> multi_polyline2d_subcatalog
        MultiPolyline2DSubcatalog(
          (is_tracking): True,
          (categories): NameList [...],
          (attributes): NameList [...]
        )

    """

    def __init__(self, is_tracking: bool = False) -> None:
        SubcatalogBase.__init__(self)
        IsTrackingMixin.__init__(self, is_tracking)


class LabeledMultiPolyline2D(  # type: ignore[misc]
    _LabelBase, MultiPolyline2D
):  # pylint: disable=too-many-ancestors
    """This class defines the concept of multiPolyline2D label.

    :class:`LabeledMultiPolyline2D` is the 2D multiple polyline type of label,
    which is often used for CV tasks such as lane detection.

    Arguments:
        polylines: A list of polylines.
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    Attributes:
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    Examples:
        >>> LabeledMultiPolyline2D(
        ...     [[[1, 2], [2, 3]], [[3, 4], [6, 8]]],
        ...     category="example",
        ...     attributes={"key": "value"},
        ...     instance="123",
        ... )
        LabeledPolyline2D [
          Polyline2D [...]
          Polyline2D [...]
        ](
          (category): 'example',
          (attributes): {...},
          (instance): '123'
        )

    """

    _T = TypeVar("_T", bound="LabeledMultiPolyline2D")

    _repr_type = ReprType.SEQUENCE
    _repr_attrs = _LabelBase._repr_attrs
    _attrs_base: MultiPolyline2D = attr_base(key="multiPolyline2d")

    def __init__(
        self,
        polylines: Optional[Iterable[Iterable[float]]] = None,
        *,
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        instance: Optional[str] = None,
    ):
        MultiPolyline2D.__init__(self, polylines)  # type: ignore[arg-type]
        _LabelBase.__init__(self, category, attributes, instance)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:  # type: ignore[override]
        """Loads a LabeledMultiPolyline2D from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the 2D polyline label.

        Returns:
            The loaded :class:`LabeledMultiPolyline2D` object.

        Examples:
            >>> contents = {
            ...     "multiPolyline2d": [[{'x': 1, 'y': 1}, {'x': 1, 'y': 2}, {'x': 2, 'y': 2}],
                                        [{'x': 2, 'y': 3}, {'x': 3, 'y': 5}]],
            ...     "category": "example",
            ...     "attributes": {"key": "value"},
            ...     "instance": "12345",
            ... }
            >>> LabeledMultiPolyline2D.loads(contents)
            LabeledMultiPolyline2D [
              Polyline2D [...]
              Polyline2D [...]
            ](
              (category): 'example',
              (attributes): {...},
              (instance): '12345'
            )

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:  # type: ignore[override]
        """Dumps the current 2D multiple polyline label into a dict.

        Returns:
            A dict containing all the information of the 2D polyline label.

        Examples:
            >>> labeledmultipolyline2d = LabeledMultiPolyline2D(
            ...     [[[1, 1], [1, 2], [2, 2]], [[2, 3], [3, 5]]],
            ...     category="example",
            ...     attributes={"key": "value"},
            ...     instance="123",
            ... )
            >>> labeledpolyline2d.dumps()
            {
                'category': 'example',
                'attributes': {'key': 'value'},
                'instance': '123',
                'polyline2d': [
                    [{'x': 1, 'y': 1}, {'x': 1, 'y': 2}, {'x': 2, 'y': 2}],
                    [{'x': 2, 'y': 3}, {'x': 3, 'y': 5}],
            }

        """
        return self._dumps()
