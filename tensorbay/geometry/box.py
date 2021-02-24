#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""This file defines class Box2D, Box3D"""

from typing import Dict, Iterable, Optional, Tuple, Type, TypeVar, Union

from ..utility import ReprMixin, ReprType, UserSequence, common_loads
from .quaternion import Quaternion
from .transform import Transform3D
from .vector import Vector2D, Vector3D

_T = TypeVar("_T", bound="Box3D")


class Box2D(UserSequence[float]):
    """Contain the definition of 2D bounding box and some related operations.

    :param args: Union[None, float, Sequence[float]],
        box = Box2D()
        box = Box2D(10, 20, 30, 40)
        box = Box2D([10, 20, 30, 40])
    :param x: X coordinate of the top left vertex of the box
    :param y: Y coordinate of the top left vertex of the box
    :param width: Length along the x axis
    :param height: Length along the y axis
    :raise TypeError: When input params do not meet the requirement
    """

    _repr_type = ReprType.INSTANCE
    _T = TypeVar("_T", bound="Box2D")

    _LENGTH = 4

    def __init__(
        self,
        *args: Union[None, float, Iterable[float]],
        x: Optional[float] = None,
        y: Optional[float] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
    ) -> None:
        if x is not None or y is not None or width is not None or height is not None:
            try:
                xmin: float = x  # type: ignore[assignment]
                ymin: float = y  # type: ignore[assignment]
                xmax = x + width  # type: ignore[operator]
                ymax = y + height  # type: ignore[operator]
            except TypeError as error:
                raise TypeError(
                    "Require x, y, width, height keyword arguments to construct a 2D box."
                ) from error
        else:
            arg: Optional[Iterable[float]]
            arg = args[0] if len(args) == 1 else args  # type: ignore[assignment]
            if arg is None:
                self._data = (0.0,) * Box2D._LENGTH
                return

            try:
                xmin, ymin, xmax, ymax = arg
            except (ValueError, TypeError) as error:
                raise TypeError(
                    f"Require 4 dimensional data to construct {self.__class__.__name__}."
                ) from error

        if xmin >= xmax or ymin >= ymax:
            self._data = (0.0,) * Box2D._LENGTH
        else:
            self._data = (xmin, ymin, xmax, ymax)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, float]) -> _T:
        """Load a Box2D from a dict containing coordinates of the 2D box.

        :param contents: A dict containing coordinates of a 2D box
        {
            "xmin": ...
            "ymin": ...
            "xmax": ...
            "ymax": ...
        }
        :return: The loaded Box2D
        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, float]) -> None:
        self._data = (contents["xmin"], contents["ymin"], contents["xmax"], contents["ymax"])

    def _repr_head(self) -> str:
        """return basic info of the Box2D.

        :return: basic info of the Box2D
        """
        return f"{self.__class__.__name__}{self._data}"

    def dumps(self) -> Dict[str, float]:
        """Dump a 2D box as a dict.

        :return: a dict containing vertex coordinates of the box
        """
        return {
            "xmin": self._data[0],
            "ymin": self._data[1],
            "xmax": self._data[2],
            "ymax": self._data[3],
        }

    def __and__(self, other: "Box2D") -> "Box2D":
        """Calculate the intersect box of two boxes.

        :param other: the other box
        :return: the intersect box of the two boxes
        """
        xmin = max(self._data[0], other._data[0])
        ymin = max(self._data[1], other._data[1])
        xmax = min(self._data[2], other._data[2])
        ymax = min(self._data[3], other._data[3])
        return Box2D(xmin, ymin, xmax, ymax)

    def __len__(self) -> int:
        return Box2D._LENGTH

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self._data.__eq__(other._data)
        return False

    @property
    def xmin(self) -> float:
        """Get the minimum x coordinate.

        :return: minimum x coordinate
        """
        return self._data[0]

    @property
    def ymin(self) -> float:
        """Get the minimum y coordinate.

        :return: minimum y coordinate
        """
        return self._data[1]

    @property
    def xmax(self) -> float:
        """Get the maximum x coordinate.

        :return: maximum x coordinate
        """
        return self._data[2]

    @property
    def ymax(self) -> float:
        """Get the maximum y coordinate.

        :return: maximum y coordinate
        """
        return self._data[3]

    @property
    def tl(self) -> Vector2D:  # pylint: disable=invalid-name
        """Get the top left point.

        :return: the top left point
        """
        return Vector2D(self._data[:2])

    @property
    def br(self) -> Vector2D:  # pylint: disable=invalid-name
        """Get the bottom right point.

        :return: the bottom right point
        """
        return Vector2D(self._data[2:])

    @property
    def width(self) -> float:
        """Get the width of the 2d box"""
        return self._data[2] - self._data[0]

    @property
    def height(self) -> float:
        """Get the height of the 2d box"""
        return self._data[3] - self._data[1]

    def area(self) -> float:
        """Get the area of the 2d box"""
        return self.width * self.height

    @staticmethod
    def iou(box1: "Box2D", box2: "Box2D") -> float:
        """Calculate the intersection over union of two 2d boxes.

        :param box1: a 2d box
        :param box2: a 2d box
        :return: intersection over union between the two input boxes
        """
        area1 = box1.area()
        area2 = box2.area()
        intersect_box = box1 & box2
        intersect = intersect_box.area()
        union = area1 + area2 - intersect
        return intersect / union


class Box3D(ReprMixin):
    """Contain the definition of 3D bounding box and some related operations.

    :param transform: A Transform3D object or a 4x4 or 3x4 transfrom matrix
    :param translation: Translation in a sequence of [x, y, z]
    :param rotation: Rotation in a sequence of [w, x, y, z] or 3x3 rotation matrix or `Quaternion`
    :param size: Size in a sequence of [x, y, z]
    :param kwargs: Other parameters to initialize rotation of the transform
    """

    _repr_type = ReprType.INSTANCE
    _repr_attrs: Tuple[str, ...] = ("translation", "rotation", "size")

    def __init__(
        self,
        transform: Transform3D.TransformType = None,
        *,
        translation: Optional[Iterable[float]] = None,
        rotation: Quaternion.ArgsType = None,
        size: Optional[Iterable[float]] = None,
        **kwargs: Quaternion.KwargsType,
    ) -> None:
        self._transform = Transform3D(
            transform, translation=translation, rotation=rotation, **kwargs
        )
        self._size = Vector3D(size)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Dict[str, float]]) -> _T:
        """Load a Box3D from a dict containing coordinates of the 3D box.

        :param contents: A dict containing coordinates of a 3D box
        {
            "size": {
                "x": ...
                "y": ...
                "z": ...
            },
            "translation": {
                "x": ...
                "y": ...
                "z": ...
            },
            "rotation": {
                "w": ...
                "x": ...
                "y": ...
                "z": ...
            }
        }
        :return: The loaded Box3D
        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Dict[str, float]]) -> None:
        self._size = Vector3D.loads(contents["size"])
        self._transform = Transform3D.loads(contents)

    def dumps(self) -> Dict[str, Dict[str, float]]:
        """Dump the 3d box as a dictionary.

        :return: a dictionary containing translation, rotation and size info
        """
        contents = self._transform.dumps()
        contents["size"] = self.size.dumps()
        return contents

    def __rmul__(self: _T, other: Transform3D) -> _T:
        if isinstance(other, Transform3D):
            box: _T = object.__new__(self.__class__)
            box._transform = other * self._transform
            box._size = self._size
            return box

        return NotImplemented  # type: ignore[unreachable]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self._size.__eq__(other._size) and self._transform.__eq__(other._transform)
        return False

    @property
    def translation(self) -> Vector3D:
        """Get the translation of the 3d box by property."""
        return self._transform.translation

    @property
    def rotation(self) -> Quaternion:
        """Get the rotation of the 3d box by property."""
        return self._transform.rotation

    @property
    def transform(self) -> Transform3D:
        """Get the transform of the 3d box by property."""
        return self._transform

    @property
    def size(self) -> Vector3D:
        """Get the size of the 3d box by property."""
        return self._size

    def volume(self) -> float:
        """Get the volume of the 3d box."""
        return self.size.x * self.size.y * self.size.z

    @classmethod
    def iou(cls, box1: "Box3D", box2: "Box3D", angle_threshold: float = 5) -> float:
        """Calculate the iou between two 3d boxes.

        :param box1: a 3d box
        :param box2: a 3d box
        :param angle_threshold: the threshold of the relative angles between two input 3d boxes,
        in degree
        :return: the iou of the two 3d boxes
        """
        box2 = box1.transform.inverse() * box2
        if abs(box2.rotation.degrees) > angle_threshold:
            return 0

        intersect_size = [
            cls._line_intersect(*args) for args in zip(box1.size, box2.size, box2.translation)
        ]
        intersect = intersect_size[0] * intersect_size[1] * intersect_size[2]
        union = box1.volume() + box2.volume() - intersect
        return intersect / union

    @staticmethod
    def _line_intersect(length1: float, length2: float, midpoint_distance: float) -> float:
        """Calculate the intersect length between two parallel lines.

        :param length1: the length of line1
        :param length2: the length of line2
        :param midpoint_distance: the distance between midpoints of the two lines
        :return: the intersect length between line1 and line2
        """
        line1_min = -length1 / 2
        line1_max = length1 / 2
        line2_min = -length2 / 2 + midpoint_distance
        line2_max = length2 / 2 + midpoint_distance
        intersect_length = min(line1_max, line2_max) - max(line1_min, line2_min)
        return intersect_length if intersect_length > 0 else 0
