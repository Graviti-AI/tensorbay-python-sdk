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
from ..utility import ReprType, SubcatalogTypeRegister, TypeRegister, common_loads
from .basic import LabelType, SubcatalogBase, _LabelBase
from .supports import AttributesMixin, CategoriesMixin, IsTrackingMixin


@SubcatalogTypeRegister(LabelType.BOX2D)
class Box2DSubcatalog(  # pylint: disable=too-many-ancestors
    SubcatalogBase, IsTrackingMixin, CategoriesMixin, AttributesMixin
):
    """This class defines the subcatalog for 2D box type of labels.

    Arguments:
        is_tracking: A boolean value indicates whether the corresponding
            subcatalog contains tracking information.

    Attributes:
        description: The description of the entire 2D box subcatalog.
        categories: All the possible categories in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameOrderedDict`
            with the category names as keys
            and the :class:`~tensorbay.label.supports.CategoryInfo` as values.
        category_delimiter: The delimiter in category values indicating parent-child relationship.
        attributes: All the possible attributes in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameOrderedDict`
            with the attribute names as keys
            and the :class:`~tensorbay.label.attribute.AttributeInfo` as values.
        is_tracking: Whether the Subcatalog contains tracking information.

    """

    def __init__(self, is_tracking: bool = False) -> None:
        IsTrackingMixin.__init__(self, is_tracking)


@TypeRegister(LabelType.BOX2D)
class LabeledBox2D(Box2D, _LabelBase):  # pylint: disable=too-many-ancestors
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

    """

    _T = TypeVar("_T", bound="LabeledBox2D")

    _repr_type = ReprType.INSTANCE
    _repr_attrs = _LabelBase._repr_attrs

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

    def _loads(self, contents: Dict[str, Any]) -> None:
        Box2D._loads(self, contents["box2d"])
        _LabelBase._loads(self, contents)

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

        """
        return cls(
            x, y, x + width, y + height, category=category, attributes=attributes, instance=instance
        )

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a LabeledBox2D from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the 2D bounding box label,
                whose format should be like::

                    {
                        "box2d": {
                            "xmin": <float>
                            "ymin": <float>
                            "xmax": <float>
                            "ymax": <float>
                        },
                        "category": <str>
                        "attributes": {
                            <key>: <value>
                            ...
                            ...
                        },
                        "instance": <str>
                    }

        Returns:
            The loaded :class:`LabeledBox2D` object.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the current 2D bounding box label into a dict.

        Returns:
            A dict containing all the information of the 2D box label,
            whose format is like::

                {
                    "box2d": {
                        "xmin": <float>
                        "ymin": <float>
                        "xmax": <float>
                        "ymax": <float>
                    },
                    "category": <str>
                    "attributes": {
                        <key>: <value>
                        ...
                        ...
                    },
                    "instance": <str>
                }

        """
        contents = _LabelBase.dumps(self)
        contents["box2d"] = Box2D.dumps(self)
        return contents


@SubcatalogTypeRegister(LabelType.BOX3D)
class Box3DSubcatalog(  # pylint: disable=too-many-ancestors
    SubcatalogBase, IsTrackingMixin, CategoriesMixin, AttributesMixin
):
    """This class defines the subcatalog for 3D box type of labels.

    Arguments:
        is_tracking: A boolean value indicates whether the corresponding
            subcatalog contains tracking information.

    Attributes:
        description: The description of the entire 3D box subcatalog.
        categories: All the possible categories in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameOrderedDict`
            with the category names as keys
            and the :class:`~tensorbay.label.supports.CategoryInfo` as values.
        category_delimiter: The delimiter in category values indicating parent-child relationship.
        attributes: All the possible attributes in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameOrderedDict`
            with the attribute names as keys
            and the :class:`~tensorbay.label.attribute.AttributeInfo` as values.
        is_tracking: Whether the Subcatalog contains tracking information.

    """

    def __init__(self, is_tracking: bool = False) -> None:
        IsTrackingMixin.__init__(self, is_tracking)


@TypeRegister(LabelType.BOX3D)
class LabeledBox3D(Box3D, _LabelBase):
    """This class defines the concept of 3D bounding box label.

    :class:`LabeledBox3D` is the 3D bounding box type of label,
    which is often used for object detection in 3D point cloud.

    Arguments:
        transform: The transform of the 3D bounding box label in
            a :class:`~tensorbay.geometry.transform.Transform3D` object
            or a 4x4 or 3x4 transformation matrix.
        translation: Translation of the 3D bounding box label in a sequence of [x, y, z].
        rotation: Rotation of the 3D bounding box label in a sequence of [w, x, y, z]
            or a 3x3 rotation matrix
            or a numpy quaternion object.
        size: Size of the 3D bounding box label in a sequence of [x, y, z].
        category: Category of the 3D bounding box label.
        attributes: Attributs of the 3D bounding box label.
        instance: The instance id of the 3D bounding box label.

    Attributes:
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.
        size: The size of the 3D bounding box.
        transform: The transform of the 3D bounding box.

    """

    _T = TypeVar("_T", bound="LabeledBox3D")

    _repr_attrs = Box3D._repr_attrs + _LabelBase._repr_attrs

    def __init__(
        self,
        transform: Transform3D.TransformType = None,
        *,
        translation: Iterable[float] = (0, 0, 0),
        rotation: Transform3D.RotationType = (1, 0, 0, 0),
        size: Iterable[float] = (0, 0, 0),
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        instance: Optional[str] = None,
    ):
        Box3D.__init__(
            self,
            transform,
            translation=translation,
            rotation=rotation,
            size=size,
        )
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

    def _loads(self, contents: Dict[str, Any]) -> None:
        Box3D._loads(self, contents["box3d"])
        _LabelBase._loads(self, contents)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a LabeledBox3D from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the 3D bounding box label,
                whose format should be like::

                    {
                        "box3d": {
                            "translation": {
                                "x": <float>
                                "y": <float>
                                "z": <float>
                            },
                            "rotation": {
                                "w": <float>
                                "x": <float>
                                "y": <float>
                                "z": <float>
                            },
                            "size": {
                                "x": <float>
                                "y": <float>
                                "z": <float>
                            }
                        },
                        "category": <str>
                        "attributes": {
                            <key>: <value>
                            ...
                            ...
                        },
                        "instance": <str>
                    }

        Returns:
            The loaded :class:`LabeledBox3D` object.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps the current 3D bounding box label into a dict.

        Returns:
            A dict containing all the information of the 3D bounding box label,
            whose format is like::

                {
                    "box3d": {
                        "translation": {
                            "x": <float>
                            "y": <float>
                            "z": <float>
                        },
                        "rotation": {
                            "w": <float>
                            "x": <float>
                            "y": <float>
                            "z": <float>
                        },
                        "size": {
                            "x": <float>
                            "y": <float>
                            "z": <float>
                        }
                    },
                    "category": <str>
                    "attributes": {
                        <key>: <value>
                        ...
                        ...
                    },
                    "instance": <str>
                },

        """
        contents = _LabelBase.dumps(self)
        contents["box3d"] = Box3D.dumps(self)
        return contents
