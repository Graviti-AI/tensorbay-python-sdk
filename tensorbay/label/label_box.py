#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""LabeledBox2D ,LabeledBox3D, Box2DSubcatalog, Box3DSubcatalog.

:class:`Box2DSubcatalog` defines the subcatalog for 2D box type of labels.

:class:`LabeledBox2D` is the 2D bounding box type of label,
which is often used for CV tasks such as object detection.

:class:`Box3DSubcatalog` defines the subcatalog for 3D box type of labels.

:class:`LabeledBox3D` is the 3D bounding box type of label,
which is often used for object detection in 3D point cloud.

"""

import warnings
from typing import Any, Dict, Iterable, Optional, Type, TypeVar

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from quaternion import quaternion

from ..geometry import Box2D, Box3D, Transform3D
from ..utility import MatrixType, ReprType, attr_base, common_loads
from .basic import SubcatalogBase, _LabelBase
from .supports import AttributesMixin, CategoriesMixin, IsTrackingMixin


class Box2DSubcatalog(SubcatalogBase, IsTrackingMixin, CategoriesMixin, AttributesMixin):
    """This class defines the subcatalog for 2D box type of labels.

    Arguments:
        is_tracking: A boolean value indicates whether the corresponding
            subcatalog contains tracking information.

    Attributes:
        description: The description of the entire 2D box subcatalog.
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
        *Initialization Method 1:* Init from ``Box2DSubcatalog.loads()`` method.

        >>> catalog = {
        ...     "BOX2D": {
        ...         "isTracking": True,
        ...         "categoryDelimiter": ".",
        ...         "categories": [{"name": "0"}, {"name": "1"}],
        ...         "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        ...     }
        ... }
        >>> Box2DSubcatalog.loads(catalog["BOX2D"])
        Box2DSubcatalog(
          (is_tracking): True,
          (category_delimiter): '.',
          (categories): NameList [...],
          (attributes): NameList [...]
        )

        *Initialization Method 2:* Init an empty Box2DSubcatalog and then add the attributes.

        >>> from tensorbay.utility import NameList
        >>> from tensorbay.label import CategoryInfo, AttributeInfo
        >>> categories = NameList()
        >>> categories.append(CategoryInfo("a"))
        >>> attributes = NameList()
        >>> attributes.append(AttributeInfo("gender", enum=["female", "male"]))
        >>> box2d_subcatalog = Box2DSubcatalog()
        >>> box2d_subcatalog.is_tracking = True
        >>> box2d_subcatalog.category_delimiter = "."
        >>> box2d_subcatalog.categories = categories
        >>> box2d_subcatalog.attributes = attributes
        >>> box2d_subcatalog
        Box2DSubcatalog(
          (is_tracking): True,
          (category_delimiter): '.',
          (categories): NameList [...],
          (attributes): NameList [...]
        )

    """

    def __init__(self, is_tracking: bool = False) -> None:
        SubcatalogBase.__init__(self)
        IsTrackingMixin.__init__(self, is_tracking)


class LabeledBox2D(_LabelBase, Box2D):  # pylint: disable=too-many-ancestors
    """This class defines the concept of 2D bounding box label.

    :class:`LabeledBox2D` is the 2D bounding box type of label,
    which is often used for CV tasks such as object detection.

    Arguments:
        xmin: The x coordinate of the top-left vertex of the labeled 2D box.
        ymin: The y coordinate of the top-left vertex of the labeled 2D box.
        xmax: The x coordinate of the bottom-right vertex of the labeled 2D box.
        ymax: The y coordinate of the bottom-right vertex of the labeled 2D box.
        category: The category of the label.
        attributes: The attributs of the label.
        instance: The instance id of the label.

    Attributes:
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    Examples:
        >>> xmin, ymin, xmax, ymax = 1, 2, 4, 4
        >>> LabeledBox2D(
        ...     xmin,
        ...     ymin,
        ...     xmax,
        ...     ymax,
        ...     category="example",
        ...     attributes={"attr": "a"},
        ...     instance="12345",
        ... )
        LabeledBox2D(1, 2, 4, 4)(
          (category): 'example',
          (attributes): {...},
          (instance): '12345'
        )

    """

    _T = TypeVar("_T", bound="LabeledBox2D")

    _repr_type = ReprType.INSTANCE
    _repr_attrs = _LabelBase._repr_attrs

    _attrs_base: Box2D = attr_base(key="box2d")

    def __init__(
        self,
        xmin: float,
        ymin: float,
        xmax: float,
        ymax: float,
        *,
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        instance: Optional[str] = None,
    ):
        Box2D.__init__(self, xmin, ymin, xmax, ymax)
        _LabelBase.__init__(self, category, attributes, instance)

    @classmethod
    def from_xywh(  # pylint: disable=arguments-differ
        cls: Type[_T],
        x: float,
        y: float,
        width: float,
        height: float,
        *,
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        instance: Optional[str] = None,
    ) -> _T:
        """Create a :class:`LabeledBox2D` instance from the top-left vertex, the width and height.

        Arguments:
            x: X coordinate of the top left vertex of the box.
            y: Y coordinate of the top left vertex of the box.
            width: Length of the box along the x axis.
            height: Length of the box along the y axis.
            category: The category of the label.
            attributes: The attributs of the label.
            instance: The instance id of the label.

        Returns:
            The created :class:`LabeledBox2D` instance.

        Examples:
            >>> x, y, width, height = 1, 2, 3, 4
            >>> LabeledBox2D.from_xywh(
            ...     x,
            ...     y,
            ...     width,
            ...     height,
            ...     category="example",
            ...     attributes={"key": "value"},
            ...     instance="12345",
            ... )
            LabeledBox2D(1, 2, 4, 6)(
              (category): 'example',
              (attributes): {...},
              (instance): '12345'
            )

        """
        return cls(
            x, y, x + width, y + height, category=category, attributes=attributes, instance=instance
        )

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a LabeledBox2D from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the 2D bounding box label.

        Returns:
            The loaded :class:`LabeledBox2D` object.

        Examples:
            >>> contents = {
            ...     "box2d": {"xmin": 1, "ymin": 2, "xmax": 5, "ymax": 8},
            ...     "category": "example",
            ...     "attributes": {"key": "value"},
            ...     "instance": "12345",
            ... }
            >>> LabeledBox2D.loads(contents)
            LabeledBox2D(1, 2, 5, 8)(
              (category): 'example',
              (attributes): {...},
              (instance): '12345'
            )

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the current 2D bounding box label into a dict.

        Returns:
            A dict containing all the information of the 2D box label.

        Examples:
            >>> xmin, ymin, xmax, ymax = 1, 2, 4, 4
            >>> labelbox2d = LabeledBox2D(
            ...     xmin,
            ...     ymin,
            ...     xmax,
            ...     ymax,
            ...     category="example",
            ...     attributes={"attr": "a"},
            ...     instance="12345",
            ... )
            >>> labelbox2d.dumps()
            {
                'category': 'example',
                'attributes': {'attr': 'a'},
                'instance': '12345',
                'box2d': {'xmin': 1, 'ymin': 2, 'xmax': 4, 'ymax': 4},
            }

        """
        return self._dumps()


class Box3DSubcatalog(SubcatalogBase, IsTrackingMixin, CategoriesMixin, AttributesMixin):
    """This class defines the subcatalog for 3D box type of labels.

    Arguments:
        is_tracking: A boolean value indicates whether the corresponding
            subcatalog contains tracking information.

    Attributes:
        description: The description of the entire 3D box subcatalog.
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
        *Initialization Method 1:* Init from ``Box3DSubcatalog.loads()`` method.

        >>> catalog = {
        ...     "BOX3D": {
        ...         "isTracking": True,
        ...         "categoryDelimiter": ".",
        ...         "categories": [{"name": "0"}, {"name": "1"}],
        ...         "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        ...     }
        ... }
        >>> Box3DSubcatalog.loads(catalog["BOX3D"])
        Box3DSubcatalog(
          (is_tracking): True,
          (category_delimiter): '.',
          (categories): NameList [...],
          (attributes): NameList [...]
        )

        *Initialization Method 2:* Init an empty Box3DSubcatalog and then add the attributes.

        >>> from tensorbay.utility import NameList
        >>> from tensorbay.label import CategoryInfo, AttributeInfo
        >>> categories = NameList()
        >>> categories.append(CategoryInfo("a"))
        >>> attributes = NameList()
        >>> attributes.append(AttributeInfo("gender", enum=["female", "male"]))
        >>> box3d_subcatalog = Box3DSubcatalog()
        >>> box3d_subcatalog.is_tracking = True
        >>> box3d_subcatalog.category_delimiter = "."
        >>> box3d_subcatalog.categories = categories
        >>> box3d_subcatalog.attributes = attributes
        >>> box3d_subcatalog
        Box3DSubcatalog(
          (is_tracking): True,
          (category_delimiter): '.',
          (categories): NameList [...],
          (attributes): NameList [...]
        )

    """

    def __init__(self, is_tracking: bool = False) -> None:
        SubcatalogBase.__init__(self)
        IsTrackingMixin.__init__(self, is_tracking)


class LabeledBox3D(_LabelBase, Box3D):
    """This class defines the concept of 3D bounding box label.

    :class:`LabeledBox3D` is the 3D bounding box type of label,
    which is often used for object detection in 3D point cloud.

    Arguments:
        size: Size of the 3D bounding box label in a sequence of [x, y, z].
        translation: Translation of the 3D bounding box label in a sequence of [x, y, z].
        rotation: Rotation of the 3D bounding box label in a sequence of [w, x, y, z]
            or a numpy quaternion object.
        transform_matrix: A 4x4 or 3x4 transformation matrix.
        category: Category of the 3D bounding box label.
        attributes: Attributs of the 3D bounding box label.
        instance: The instance id of the 3D bounding box label.

    Attributes:
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.
        size: The size of the 3D bounding box.
        transform: The transform of the 3D bounding box.

    Examples:
        >>> LabeledBox3D(
        ...     size=[1, 2, 3],
        ...     translation=(1, 2, 3),
        ...     rotation=(0, 1, 0, 0),
        ...     category="example",
        ...     attributes={"key": "value"},
        ...     instance="12345",
        ... )
        LabeledBox3D(
          (size): Vector3D(1, 2, 3),
          (translation): Vector3D(1, 2, 3),
          (rotation): quaternion(0, 1, 0, 0),
          (category): 'example',
          (attributes): {...},
          (instance): '12345'
        )

    """

    _T = TypeVar("_T", bound="LabeledBox3D")

    _repr_attrs = Box3D._repr_attrs + _LabelBase._repr_attrs

    _attrs_base: Box3D = attr_base(key="box3d")

    def __init__(
        self,
        size: Iterable[float],
        translation: Iterable[float] = (0, 0, 0),
        rotation: Transform3D.RotationType = (1, 0, 0, 0),
        *,
        transform_matrix: Optional[MatrixType] = None,
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        instance: Optional[str] = None,
    ):
        Box3D.__init__(self, size, translation, rotation, transform_matrix=transform_matrix)
        _LabelBase.__init__(self, category, attributes, instance)

    def __rmul__(self: _T, other: Transform3D) -> _T:
        if isinstance(other, (Transform3D, quaternion)):
            labeled_box_3d = Box3D.__rmul__(self, other)
            if hasattr(self, "category"):
                labeled_box_3d.category = self.category
            if hasattr(self, "attributes"):
                labeled_box_3d.attributes = self.attributes
            if hasattr(self, "instance"):
                labeled_box_3d.instance = self.instance
            return labeled_box_3d

        return NotImplemented  # type: ignore[unreachable]

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a LabeledBox3D from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the 3D bounding box label.

        Returns:
            The loaded :class:`LabeledBox3D` object.

        Examples:
            >>> contents = {
            ...     "box3d": {
            ...         "size": {"x": 1, "y": 2, "z": 3},
            ...         "translation": {"x": 1, "y": 2, "z": 3},
            ...         "rotation": {"w": 1, "x": 0, "y": 0, "z": 0},
            ...     },
            ...     "category": "test",
            ...     "attributes": {"key": "value"},
            ...     "instance": "12345",
            ... }
            >>> LabeledBox3D.loads(contents)
            LabeledBox3D(
              (size): Vector3D(1, 2, 3),
              (translation): Vector3D(1, 2, 3),
              (rotation): quaternion(1, 0, 0, 0),
              (category): 'test',
              (attributes): {...},
              (instance): '12345'
            )

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the current 3D bounding box label into a dict.

        Returns:
            A dict containing all the information of the 3D bounding box label.

        Examples:
            >>> labeledbox3d = LabeledBox3D(
            ...     size=[1, 2, 3],
            ...     translation=(1, 2, 3),
            ...     rotation=(0, 1, 0, 0),
            ...     category="example",
            ...     attributes={"key": "value"},
            ...     instance="12345",
            ... )
            >>> labeledbox3d.dumps()
            {
                'category': 'example',
                'attributes': {'key': 'value'},
                'instance': '12345',
                'box3d': {
                    'translation': {'x': 1, 'y': 2, 'z': 3},
                    'rotation': {'w': 0.0, 'x': 1.0, 'y': 0.0, 'z': 0.0},
                    'size': {'x': 1, 'y': 2, 'z': 3},
                },
            }

        """
        return self._dumps()
