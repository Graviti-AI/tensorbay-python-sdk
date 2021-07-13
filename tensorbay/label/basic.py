#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""LabelType, SubcatalogBase.

:class:`LabelType` is an enumeration type
which includes all the supported label types within :class:`Label`.

:class:`Subcatalogbase` is the base class for different types of subcatalogs,
which defines the basic concept of Subcatalog.

A subcatalog class extends :class:`SubcatalogBase` and needed :class:`SubcatalogMixin` classes.

"""

from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union

from ..utility import AttrsMixin, ReprMixin, ReprType, TypeEnum, TypeMixin, attr, common_loads


class LabelType(TypeEnum):
    """This class defines all the supported types within :class:`Label`.

    Examples:
        >>> LabelType.BOX3D
        <LabelType.BOX3D: 'box3d'>
        >>> LabelType["BOX3D"]
        <LabelType.BOX3D: 'box3d'>
        >>> LabelType.BOX3D.name
        'BOX3D'
        >>> LabelType.BOX3D.value
        'box3d'

    """

    __subcatalog_registry__: Dict[TypeEnum, Type[Any]] = {}

    CLASSIFICATION = "classification"
    BOX2D = "box2d"
    BOX3D = "box3d"
    POLYGON = "polygon"
    POLYLINE2D = "polyline2d"
    KEYPOINTS2D = "keypoints2d"
    SENTENCE = "sentence"

    @property
    def subcatalog_type(self) -> Type[Any]:
        """Return the corresponding subcatalog class.

        Each label type has a corresponding Subcatalog class.

        Returns:
            The corresponding subcatalog type.

        Examples:
            >>> LabelType.BOX3D.subcatalog_type
            <class 'tensorbay.label.label_box.Box3DSubcatalog'>

        """
        return self.__subcatalog_registry__[self]


class SubcatalogBase(TypeMixin[LabelType], ReprMixin, AttrsMixin):
    """This is the base class for different types of subcatalogs.

    It defines the basic concept of Subcatalog, which is the collection of the labels information.
    Subcatalog contains the features, fields and specific definitions of the labels.

    The Subcatalog format varies by label type.

    Arguments:
        description: The description of the entire subcatalog.

    Attributes:
        description: The description of the entire subcatalog.

    """

    _T = TypeVar("_T", bound="SubcatalogBase")

    _repr_type = ReprType.INSTANCE
    _repr_attrs = (
        "is_sample",
        "sample_rate",
        "is_tracking",
        "keypoints",
        "category_delimiter",
        "categories",
        "attributes",
        "lexicon",
    )
    description: str = attr(default="")

    def __init__(self, description: str = "") -> None:
        self.description = description

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a subcatalog from a dict containing the information of the subcatalog.

        Arguments:
            contents: A dict containing the information of the subcatalog.

        Returns:
            The loaded :class:`SubcatalogBase` object.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps all the information of the subcatalog into a dict.

        Returns:
            A dict containing all the information of the subcatalog.

        """
        return self._dumps()


class _LabelBase(AttrsMixin, TypeMixin[LabelType], ReprMixin):
    """This class defines the basic concept of label.

    :class:`_LabelBase` is the most basic label level in the TensorBay dataset structure,
    and is the base class for the following various types of label classes.

    Each :class:`_LabelBase` object
    contains one annotaion of a :class:`~tensorbay.dataset.data.Data` object.

    Arguments:
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    Attributes:
        category: The category of the label.
        attributes: The attributes of the label.
        instance: The instance id of the label.

    """

    _label_attrs: Tuple[str, ...] = ("category", "attributes", "instance")

    _repr_attrs = _label_attrs

    _AttributeType = Dict[str, Union[str, int, float, bool, List[Union[str, int, float, bool]]]]

    category: str = attr(is_dynamic=True)
    attributes: _AttributeType = attr(is_dynamic=True)
    instance: str = attr(is_dynamic=True)

    def __init__(
        self,
        category: Optional[str] = None,
        attributes: Optional[_AttributeType] = None,
        instance: Optional[str] = None,
    ):
        if category:
            self.category = category
        if attributes:
            self.attributes = attributes
        if instance:
            self.instance = instance

    def dumps(self) -> Dict[str, Any]:
        """Dumps the label into a dict.

        Returns:
            A dict containing all the information of the label.
            See dict format details in ``dumps()`` of different label classes .

        """
        return self._dumps()
