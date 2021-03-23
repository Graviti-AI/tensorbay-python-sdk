#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""LabelType, SubcatalogBase, Label.

:class:`LabelType` is an enumeration type
which includes all the supported label types within :class:`Label`.

:class:`Subcatalogbase` is the base class for different types of subcatalogs,
which defines the basic concept of Subcatalog.

A :class:`~.tensorbay.dataset.data.Data` instance contains one or several types of labels,
all of which are stored in :attr:`~tensorbay.dataset.data.Data.label`.

A subcatalog class extends :class:`SubcatalogBase` and needed :class:`SubcatalogMixin` classes.

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

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type, TypeVar

from ..utility import EqMixin, ReprMixin, ReprType, TypeEnum, TypeMixin, common_loads
from .supports import SubcatalogMixin

if TYPE_CHECKING:
    from .label_box import LabeledBox2D, LabeledBox3D
    from .label_classification import Classification
    from .label_keypoints import LabeledKeypoints2D
    from .label_polygon import LabeledPolygon2D
    from .label_polyline import LabeledPolyline2D
    from .label_sentence import LabeledSentence


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

        Examples:
            >>> LabelType.BOX3D.subcatalog_type
            <class 'tensorbay.label.label_box.Box3DSubcatalog'>

        """
        return self.__subcatalog_registry__[self]


class SubcatalogBase(TypeMixin[LabelType], ReprMixin, EqMixin):
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

    _supports: Tuple[Type[SubcatalogMixin], ...]

    description = ""

    def __init_subclass__(cls) -> None:
        cls._supports = tuple(
            filter(lambda class_: issubclass(class_, SubcatalogMixin), cls.__bases__)
        )

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


class _LabelBase(TypeMixin[LabelType], ReprMixin, EqMixin):
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


class Label(ReprMixin, EqMixin):
    """This class defines :attr:`~tensorbay.dataset.data.Data.label`.

    It contains growing types of labels referring to different tasks.

    Examples:
        >>> from tensorbay.label import Classification
        >>> label = Label()
        >>> label.classification = Classification("example_category", {"example_attribute1": "a"})
        >>> label
        Label(
          (classification): Classification(
            (category): 'example_category',
            (attributes): {...}
          )
        )

    """

    _T = TypeVar("_T", bound="Label")

    _repr_type = ReprType.INSTANCE
    _repr_attrs = tuple(label_type.value for label_type in LabelType)
    _repr_maxlevel = 2

    classification: "Classification"
    box2d: List["LabeledBox2D"]
    box3d: List["LabeledBox3D"]
    polygon2d: List["LabeledPolygon2D"]
    polyline2d: List["LabeledPolyline2D"]
    keypoints2d: List["LabeledKeypoints2D"]
    sentence: List["LabeledSentence"]

    def __bool__(self) -> bool:
        for label_type in LabelType:
            if hasattr(self, label_type.value):
                return True
        return False

    def _loads(self, contents: Dict[str, Any]) -> None:
        for key, labels in contents.items():
            if key not in LabelType.__members__:
                continue

            label_type = LabelType[key]
            if label_type == LabelType.CLASSIFICATION:
                setattr(self, label_type.value, label_type.type.loads(labels))
            else:
                setattr(
                    self,
                    label_type.value,
                    [label_type.type.loads(label) for label in labels],
                )

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads data from a dict containing the labels information.

        Arguments:
            contents: A dict containing the labels information.

        Returns:
            A :class:`Label` instance containing labels information from the given dict.

        Examples:
            >>> contents = {
            ...     "CLASSIFICATION": {
            ...         "category": "example_category",
            ...         "attributes": {"example_attribute1": "a"}
            ...     }
            ... }
            >>> Label.loads(contents)
            Label(
              (classification): Classification(
                (category): 'example_category',
                (attributes): {...}
              )
            )

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps all labels into a dict.

        Returns:
            Dumped labels dict.

        Examples:
            >>> from tensorbay.label import Classification
            >>> label = Label()
            >>> label.classification = Classification("category1", {"attribute1": "a"})
            >>> label.dumps()
            {'CLASSIFICATION': {'category': 'category1', 'attributes': {'attribute1': 'a'}}}

        """
        contents: Dict[str, Any] = {}
        for label_type in LabelType:
            labels = getattr(self, label_type.value, None)
            if labels is None:
                continue
            if label_type == LabelType.CLASSIFICATION:
                contents[label_type.name] = labels.dumps()
            else:
                contents[label_type.name] = [label.dumps() for label in labels]

        return contents
