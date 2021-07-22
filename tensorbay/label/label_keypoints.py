#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""LabeledKeypoints2D, Keypoints2DSubcatalog.

:class:`Keypoints2DSubcatalog` defines the subcatalog for 2D keypoints type of labels.

:class:`LabeledKeypoints2D` is the 2D keypoints type of label,
which is often used for CV tasks such as human body pose estimation.

"""

from typing import Any, Dict, Iterable, List, Optional, Type, TypeVar, Union

from ..geometry import Keypoints2D
from ..utility import ReprType, attr, attr_base, common_loads
from .basic import SubcatalogBase, _LabelBase
from .supports import AttributesMixin, CategoriesMixin, IsTrackingMixin, KeypointsInfo


class Keypoints2DSubcatalog(SubcatalogBase, IsTrackingMixin, CategoriesMixin, AttributesMixin):
    """This class defines the subcatalog for 2D keypoints type of labels.

    Arguments:
        is_tracking: A boolean value indicates whether the corresponding
            subcatalog contains tracking information.

    Attributes:
        description: The description of the entire 2D keypoints subcatalog.
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
        *Initialization Method 1:* Init from ``Keypoints2DSubcatalog.loads()`` method.

        >>> catalog = {
        ...     "KEYPOINTS2D": {
        ...         "isTracking": True,
        ...         "categories": [{"name": "0"}, {"name": "1"}],
        ...         "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        ...         "keypoints": [
        ...             {
        ...                 "number": 2,
        ...                  "names": ["L_shoulder", "R_Shoulder"],
        ...                  "skeleton": [(0, 1)],
        ...             }
        ...         ],
        ...     }
        ... }
        >>> Keypoints2DSubcatalog.loads(catalog["KEYPOINTS2D"])
        Keypoints2DSubcatalog(
          (is_tracking): True,
          (keypoints): [...],
          (categories): NameList [...],
          (attributes): NameList [...]
        )

        *Initialization Method 2:* Init an empty Keypoints2DSubcatalog and then add the attributes.

        >>> from tensorbay.label import CategoryInfo, AttributeInfo, KeypointsInfo
        >>> from tensorbay.utility import NameList
        >>> categories = NameList()
        >>> categories.append(CategoryInfo("a"))
        >>> attributes = NameList()
        >>> attributes.append(AttributeInfo("gender", enum=["female", "male"]))
        >>> keypoints2d_subcatalog = Keypoints2DSubcatalog()
        >>> keypoints2d_subcatalog.is_tracking = True
        >>> keypoints2d_subcatalog.categories = categories
        >>> keypoints2d_subcatalog.attributes = attributes
        >>> keypoints2d_subcatalog.add_keypoints(
        ...     2,
        ...     names=["L_shoulder", "R_Shoulder"],
        ...     skeleton=[(0,1)],
        ...     visible="BINARY",
        ...     parent_categories="shoulder",
        ...     description="12345",
        ... )
        >>> keypoints2d_subcatalog
        Keypoints2DSubcatalog(
          (is_tracking): True,
          (keypoints): [...],
          (categories): NameList [...],
          (attributes): NameList [...]
        )

    """

    _keypoints: List[KeypointsInfo] = attr(key="keypoints")

    def __init__(self, is_tracking: bool = False) -> None:
        SubcatalogBase.__init__(self)
        IsTrackingMixin.__init__(self, is_tracking)
        self._keypoints: List[KeypointsInfo] = []

    @property
    def keypoints(self) -> List[KeypointsInfo]:
        """Return the KeypointsInfo of the Subcatalog.

        Returns:
            A list of :class:`~tensorbay.label.supports.KeypointsInfo`.

        Examples:
            >>> keypoints2d_subcatalog = Keypoints2DSubcatalog()
            >>> keypoints2d_subcatalog.add_keypoints(2)
            >>> keypoints2d_subcatalog.keypoints
            [KeypointsInfo(
              (number): 2
            )]

        """
        return self._keypoints

    def add_keypoints(
        self,
        number: int,
        *,
        names: Optional[Iterable[str]] = None,
        skeleton: Optional[Iterable[Iterable[int]]] = None,
        visible: Optional[str] = None,
        parent_categories: Union[None, str, Iterable[str]] = None,
        description: str = "",
    ) -> None:
        """Add a type of keypoints to the subcatalog.

        Arguments:
            number: The number of keypoints.
            names: All the names of keypoints.
            skeleton: The skeleton of the keypoints
                indicating which keypoint should connect with another.
            visible: The visible type of the keypoints, can only be 'BINARY' or 'TERNARY'.
                It determines the range of the
                :attr:`Keypoint2D.v<tensorbay.geometry.keypoint.Keypoint2D.v>`.
            parent_categories: The parent categories of the keypoints.
            description: The description of keypoints.

        Examples:
            >>> keypoints2d_subcatalog = Keypoints2DSubcatalog()
            >>> keypoints2d_subcatalog.add_keypoints(
            ...     2,
            ...     names=["L_shoulder", "R_Shoulder"],
            ...     skeleton=[(0,1)],
            ...     visible="BINARY",
            ...     parent_categories="shoulder",
            ...     description="12345",
            ... )
            >>> keypoints2d_subcatalog.keypoints
            [KeypointsInfo(
              (number): 2,
              (names): [...],
              (skeleton): [...],
              (visible): 'BINARY',
              (parent_categories): [...]
            )]

        """
        self._keypoints.append(
            KeypointsInfo(
                number=number,
                names=names,
                skeleton=skeleton,
                visible=visible,
                parent_categories=parent_categories,
                description=description,
            )
        )

    def dumps(self) -> Dict[str, Any]:
        """Dumps all the information of the keypoints into a dict.

        Returns:
            A dict containing all the information of this Keypoints2DSubcatalog.

        Examples:
            >>> # keypoints2d_subcatalog is the instance initialized above.
            >>> keypoints2d_subcatalog.dumps()
            {
                'isTracking': True,
                'categories': [{'name': 'a'}],
                'attributes': [{'name': 'gender', 'enum': ['female', 'male']}],
                'keypoints': [
                    {
                        'number': 2,
                        'names': ['L_shoulder', 'R_Shoulder'],
                        'skeleton': [(0, 1)],
                    }
                ]
            }

        """
        return self._dumps()


class LabeledKeypoints2D(_LabelBase, Keypoints2D):  # pylint: disable=too-many-ancestors
    """This class defines the concept of 2D keypoints label.

    :class:`LabeledKeypoints2D` is the 2D keypoints type of label,
    which is often used for CV tasks such as human body pose estimation.

    Arguments:
        keypoints: A list of 2D keypoint.
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    Attributes:
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    Examples:
        >>> LabeledKeypoints2D(
        ...     [(1, 2), (2, 3)],
        ...     category="example",
        ...     attributes={"key": "value"},
        ...     instance="123",
        ... )
        LabeledKeypoints2D [
          Keypoint2D(1, 2),
          Keypoint2D(2, 3)
        ](
          (category): 'example',
          (attributes): {...},
          (instance): '123'
        )

    """

    _T = TypeVar("_T", bound="LabeledKeypoints2D")

    _repr_type = ReprType.SEQUENCE
    _repr_attrs = _LabelBase._repr_attrs
    _attrs_base: Keypoints2D = attr_base(key="keypoints2d")

    def __init__(
        self,
        keypoints: Optional[Iterable[Iterable[float]]] = None,
        *,
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        instance: Optional[str] = None,
    ) -> None:
        Keypoints2D.__init__(self, keypoints)  # type: ignore[arg-type]
        _LabelBase.__init__(self, category, attributes, instance)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:  # type: ignore[override]
        """Loads a LabeledKeypoints2D from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the 2D keypoints label.

        Returns:
            The loaded :class:`LabeledKeypoints2D` object.

        Examples:
            >>> contents = {
            ...     "keypoints2d": [
            ...         {"x": 1, "y": 1, "v": 2},
            ...         {"x": 2, "y": 2, "v": 2},
            ...     ],
            ...     "category": "example",
            ...     "attributes": {"key": "value"},
            ...     "instance": "12345",
            ... }
            >>> LabeledKeypoints2D.loads(contents)
            LabeledKeypoints2D [
              Keypoint2D(1, 1, 2),
              Keypoint2D(2, 2, 2)
            ](
              (category): 'example',
              (attributes): {...},
              (instance): '12345'
            )

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:  # type: ignore[override]
        """Dumps the current 2D keypoints label into a dict.

        Returns:
            A dict containing all the information of the 2D keypoints label.

        Examples:
            >>> labeledkeypoints2d = LabeledKeypoints2D(
            ...     [(1, 1, 2), (2, 2, 2)],
            ...     category="example",
            ...     attributes={"key": "value"},
            ...     instance="123",
            ... )
            >>> labeledkeypoints2d.dumps()
            {
                'category': 'example',
                'attributes': {'key': 'value'},
                'instance': '123',
                'keypoints2d': [{'x': 1, 'y': 1, 'v': 2}, {'x': 2, 'y': 2, 'v': 2}],
            }

        """
        return self._dumps()
