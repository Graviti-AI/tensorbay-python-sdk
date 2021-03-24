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
from ..utility import ReprType, SubcatalogTypeRegister, TypeRegister, common_loads
from .basic import LabelType, SubcatalogBase, _LabelBase
from .supports import AttributesMixin, CategoriesMixin, IsTrackingMixin, KeypointsInfo


@SubcatalogTypeRegister(LabelType.KEYPOINTS2D)
class Keypoints2DSubcatalog(  # pylint: disable=too-many-ancestors
    SubcatalogBase, IsTrackingMixin, CategoriesMixin, AttributesMixin
):
    """This class defines the subcatalog for 2D keypoints type of labels.

    Arguments:
        is_tracking: A boolean value indicates whether the corresponding
            subcatalog contains tracking information.

    Attributes:
        description: The description of the entire 2D keypoints subcatalog.
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
        self._keypoints: List[KeypointsInfo] = []

    def _loads(self, contents: Dict[str, Any]) -> None:
        super()._loads(contents)
        self._keypoints = []
        for keypoint in contents["keypoints"]:
            self._keypoints.append(KeypointsInfo.loads(keypoint))

    @property
    def keypoints(self) -> List[KeypointsInfo]:
        """Return the KeypointsInfo of the Subcatalog.

        Returns:
            A list of :class:`~tensorbay.label.supports.KeypointsInfo`.

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
        description: Optional[str] = None,
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

        """
        contents: Dict[str, Any] = super().dumps()
        if self._keypoints:
            contents["keypoints"] = [keypoint.dumps() for keypoint in self._keypoints]
        return contents


@TypeRegister(LabelType.KEYPOINTS2D)
class LabeledKeypoints2D(Keypoints2D, _LabelBase):  # pylint: disable=too-many-ancestors
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

    """

    _T = TypeVar("_T", bound="LabeledKeypoints2D")

    _repr_type = ReprType.SEQUENCE
    _repr_attrs = _LabelBase._repr_attrs

    def __init__(
        self,
        keypoints: Optional[Iterable[Iterable[float]]] = None,
        *,
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        instance: Optional[str] = None,
    ) -> None:
        super().__init__(keypoints)
        _LabelBase.__init__(self, category, attributes, instance)

    def _loads(self, contents: Dict[str, Any]) -> None:  # type: ignore[override]
        super()._loads(contents["keypoints2d"])
        _LabelBase._loads(self, contents)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:  # type: ignore[override]
        """Loads a LabeledKeypoints2D from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the 2D keypoints label,
                whose format should be like::

                    {
                        "keypoints2d": [
                            { "x": <float>
                              "y": <float>
                              "v": <int>
                            },
                            ...
                            ...
                        ],
                        "category": <str>
                        "attributes": {
                            <key>: <value>
                            ...
                            ...
                        },
                        "instance": <str>
                    }

        Returns:
            The loaded :class:`LabeledKeypoints2D` object.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:  # type: ignore[override]
        """Dumps the current 2D keypoints label into a dict.

        Returns:
            A dict containing all the information of the 2D keypoints label,
            whose format is like::

                {
                    "keypoints2d": [
                        { "x": <float>
                          "y": <float>
                          "v": <int>
                        },
                        ...
                        ...
                    ],
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
        contents["keypoints2d"] = super().dumps()

        return contents
