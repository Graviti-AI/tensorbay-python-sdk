#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""LabelType, SubcatalogBase.

:class:`LabelType` is an enumeration type
which includes all the supported label types within :class:`~tensorbay.dataset.data.Label`.

:class:`Subcatalogbase` is the base class for different types of subcatalogs,
which defines the basic concept of Subcatalog.

A subcatalog class extends :class:`SubcatalogBase` and needed :class:`Supports` mixin classes.

Different label types correspond to different label classes classes.

.. table:: label classes
   :widths: auto

   ============================================================= ===================================
   label classes                                                 explaination
   ============================================================= ===================================
   :class:`~tensorbay.label.label_classification.Classification` classification type of label
   :class:`~tensorbay.label.label_box.LabeledBox2D`              2D bounding box type of label
   :class:`~tensorbay.label.label_box.LabeledBox3D`              3D bounding box type of label
   :class:`~tensorbay.label.label_polygon.LabeledPolygon2D`      2D polygon type of label
   :class:`~tensorbay.label.label_polyline.LabeledPolyline2D`    2D polyline type of label
   :class:`~tensorbay.label.label_keypoints.LabeledKeypoints2D`  2D keypoints type of label
   :class:`~tensorbay.label.label_sentence.LabeledSentence`      transcripted sentence type of label
   ============================================================= ===================================

"""

from typing import Any, Dict, Optional, Tuple, Type, TypeVar

from ..utility import ReprMixin, ReprType, TypeEnum, TypeMixin, common_loads
from .supports import Supports


class LabelType(TypeEnum):
    """This class defines all the supported types within :class:`~tensorbay.dataset.data.Label`."""

    __subcatalog_registry__: Dict[TypeEnum, Type[Any]] = {}

    CLASSIFICATION = "classification"
    BOX2D = "box2d"
    BOX3D = "box3d"
    POLYGON2D = "polygon2d"
    POLYLINE2D = "polyline2d"
    KEYPOINTS2D = "keypoints2d"
    SENTENCE = "sentence"

    @property
    def subcatalog_type(self) -> Type[Any]:
        """Return the corresponding subcatalog class.

        Each label type has a corresponding Subcatalog class.

        Returns:
            The corresponding subcatalog type.
        """
        return self.__subcatalog_registry__[self]


class SubcatalogBase(TypeMixin[LabelType], ReprMixin):
    """This is the base class for different types of subcatalogs.

    It defines the basic concept of Subcatalog, which is the collection of the labels information.
    Subcatalog contains the features, fields and specific definitions of the labels.

    The Subcatalog format varies by label type.

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

    _supports: Tuple[Type[Supports], ...]

    description = ""

    def __init_subclass__(cls) -> None:
        cls._supports = tuple(filter(lambda class_: issubclass(class_, Supports), cls.__bases__))

    def _loads(self, contents: Dict[str, Any]) -> None:
        if "description" in contents:
            self.description = contents["description"]
        for support in self._supports:
            support._loads(self, contents)  # pylint: disable=protected-access

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
        contents: Dict[str, Any] = {}
        if self.description:
            contents["description"] = self.description

        for support in self._supports:
            contents.update(support._dumps(self))  # pylint: disable=protected-access
        return contents


class _LabelBase(TypeMixin[LabelType], ReprMixin):
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

    category: str
    attributes: Dict[str, Any]
    instance: str

    def __init__(
        self,
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        instance: Optional[str] = None,
    ):
        if category:
            self.category = category
        if attributes:
            self.attributes = attributes
        if instance:
            self.instance = instance

    def _loads(self, contents: Dict[str, Any]) -> None:
        for attribute_name in self._label_attrs:
            if attribute_name in contents:
                setattr(self, attribute_name, contents[attribute_name])

    def dumps(self) -> Dict[str, Any]:
        """Dumps the label into a dict.

        Returns:
            A dict containing all the information of the label.
            See dict format details in ``dumps()`` of different label classes .

        """
        contents: Dict[str, Any] = {}
        for attribute_name in self._label_attrs:
            attribute_value = getattr(self, attribute_name, None)
            if attribute_value:
                contents[attribute_name] = attribute_value
        return contents
