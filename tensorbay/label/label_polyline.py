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

from ..geometry import Polyline2D
from ..utility import ReprType, SubcatalogTypeRegister, TypeRegister, common_loads
from .basic import LabelType, SubcatalogBase, _LabelBase
from .supports import AttributesMixin, CategoriesMixin, IsTrackingMixin


@SubcatalogTypeRegister(LabelType.POLYLINE2D)
class Polyline2DSubcatalog(  # pylint: disable=too-many-ancestors
    SubcatalogBase, IsTrackingMixin, CategoriesMixin, AttributesMixin
):
    """This class defines the subcatalog for 2D polyline type of labels.

    Arguments:
        is_tracking: A boolean value indicates whether the corresponding
            subcatalog contains tracking information.

    Attributes:
        description: The description of the entire 2D polyline subcatalog.
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


@TypeRegister(LabelType.POLYLINE2D)
class LabeledPolyline2D(Polyline2D, _LabelBase):  # pylint: disable=too-many-ancestors
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

    """

    _T = TypeVar("_T", bound="LabeledPolyline2D")

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
        super()._loads(contents["polyline2d"])
        _LabelBase._loads(self, contents)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:  # type: ignore[override]
        """Loads a LabeledPolyline2D from a dict containing the information of the label.

        Arguments:
            contents: A dict containing the information of the 2D polyline label,
                whose format should be like::

                    {
                        "polyline": [
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
            The loaded :class:`LabeledPolyline2D` object.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:  # type: ignore[override]
        """Dumps the current 2D polyline label into a dict.

        Returns:
            A dict containing all the information of the 2D polyline label,
            whose format is like::

                {
                    "polyline": [
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
        contents["polyline2d"] = super().dumps()

        return contents
