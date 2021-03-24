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
from ..utility import ReprType, SubcatalogTypeRegister, TypeRegister, common_loads
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


@TypeRegister(LabelType.POLYGON2D)
class LabeledPolygon2D(Polygon2D, _LabelBase):  # pylint: disable=too-many-ancestors
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

    """

    _T = TypeVar("_T", bound="LabeledPolygon2D")

    _repr_type = ReprType.SEQUENCE
    _repr_attrs = _LabelBase._repr_attrs

    def __init__(
        self,
        points: Optional[Iterable[Iterable[float]]] = None,
        *,
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        instance: Optional[str] = None,
    ):
        super().__init__(points)
        _LabelBase.__init__(self, category, attributes, instance)

    def _loads(self, contents: Dict[str, Any]) -> None:  # type: ignore[override]
        super()._loads(contents["polygon2d"])
        _LabelBase._loads(self, contents)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:  # type: ignore[override]
        """Loads a LabeledPolygon2D from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the 2D polygon label,
                whose format should be like::

                    {
                        "polygon": [
                            { "x": <int>
                              "y": <int>
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
            The loaded :class:`LabeledPolygon2D` object.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:  # type: ignore[override]
        """Dumps the current 2D polygon label into a dict.

        Returns:
            A dict containing all the information of the 2D polygon label,
            whose format is like::

                {
                    "polygon": [
                        { "x": <int>
                          "y": <int>
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
        contents["polygon2d"] = super().dumps()

        return contents
