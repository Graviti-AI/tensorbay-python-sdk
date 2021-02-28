#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Subcatalogbase and Subcatalog classes for every LabelType.

:class:`Subcatalogbase` is the base class for different types of subcatalogs,
which defines the basic concept of Subcatalog.

Subcatalog contains the features, fields and specific definitions of the labels.
The Subcatalog format varies by label type.
A subcatalog class extends :class:`SubcatalogBase` and needed :class:`Supports` mixin classes.

.. table:: subcatalog classes
   :widths: auto

   =================================   ==================================================
   subcatalog classes                  explaination
   =================================   ==================================================
   :class:`ClassificationSubcatalog`   subcatalog for classification type of label
   :class:`Box2DSubcatalog`            subcatalog for 2D bounding box type of label
   :class:`Box3DSubcatalog`            subcatalog for 3D bounding box type of label
   :class:`Keypoints2DSubcatal`        subcatalog for 2D polygon type of label
   :class:`Polygon2DSubcatalogD`       subcatalog for 2D polyline type of label
   :class:`Polyline2DSubcatalo2D`      subcatalog for 2D keypoints type of label
   :class:`SentenceSubcatalog`         subcatalog for transcripted sentence type of label
   =================================   ==================================================

"""


from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, TypeVar, Union

from ..utility import ReprMixin, ReprType, SubcatalogTypeRegister, TypeMixin, common_loads
from .label import LabelType
from .supports import (
    KeypointsInfo,
    SupportAttributes,
    SupportCategories,
    SupportIsTracking,
    Supports,
)

_T = TypeVar("_T", bound="SubcatalogBase")


class SubcatalogBase(TypeMixin[LabelType], ReprMixin):
    """This is the base class for different types of subcatalogs.

    It defines the basic concept of Subcatalog, which is the collection of the labels information.
    Subcatalog contains the features, fields and specific definitions of the labels.

    The Subcatalog format varies by label type.

    Attributes:
        description: The description of the entire subcatalog.

    """

    _supports: Tuple[Type[Supports], ...]

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

    description = ""

    def __init_subclass__(cls) -> None:
        cls._supports = tuple(filter(lambda class_: issubclass(class_, Supports), cls.__bases__))

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a subcatalog from a dict containing the information of the subcatalog.

        Arguments:
            contents: A dict containing the information of the subcatalog.

        Returns:
            The loaded :class:`SubcatalogBase` object.

        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:
        if "description" in contents:
            self.description = contents["description"]
        for support in self._supports:
            support._loads(self, contents)  # pylint: disable=protected-access

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


@SubcatalogTypeRegister(LabelType.CLASSIFICATION)
class ClassificationSubcatalog(  # pylint: disable=too-many-ancestors
    SubcatalogBase, SupportCategories, SupportAttributes
):
    """This class defines the subcatalog for classification type of labels.

    Attributes:
        description: The description of the entire classification subcatalog.
        categories: All the possible categories in the corresponding dataset
            stored in a :class:`~graviti.utility.name.NameOrderedDict`
            with the category names as keys
            and the :class:`~graviti.label.supports.CategoryInfo` as values.
        category_delimiter: The delimiter in category values indicating parent-child relationship.
        attributes: All the possible attributes in the corresponding dataset
            stored in a :class:`~graviti.utility.name.NameOrderedDict`
            with the attribute names as keys
            and the :class:`~graviti.label.attribute.AttributeInfo` as values.

    """


@SubcatalogTypeRegister(LabelType.BOX2D)
class Box2DSubcatalog(  # pylint: disable=too-many-ancestors
    SubcatalogBase, SupportIsTracking, SupportCategories, SupportAttributes
):
    """This class defines the subcatalog for 2D box type of labels.

    Arguments:
        is_tracking: A boolean value indicates whether the corresponding
            subcatalog contains tracking information.

    Attributes:
        description: The description of the entire 2D box subcatalog.
        categories: All the possible categories in the corresponding dataset
            stored in a :class:`~graviti.utility.name.NameOrderedDict`
            with the category names as keys
            and the :class:`~graviti.label.supports.CategoryInfo` as values.
        category_delimiter: The delimiter in category values indicating parent-child relationship.
        attributes: All the possible attributes in the corresponding dataset
            stored in a :class:`~graviti.utility.name.NameOrderedDict`
            with the attribute names as keys
            and the :class:`~graviti.label.attribute.AttributeInfo` as values.
        is_tracking: Whether the Subcatalog contains tracking information.

    """

    def __init__(self, is_tracking: bool = False) -> None:
        SupportIsTracking.__init__(self, is_tracking)


@SubcatalogTypeRegister(LabelType.BOX3D)
class Box3DSubcatalog(  # pylint: disable=too-many-ancestors
    SubcatalogBase, SupportIsTracking, SupportCategories, SupportAttributes
):
    """This class defines the subcatalog for 3D box type of labels.

    Arguments:
        is_tracking: A boolean value indicates whether the corresponding
            subcatalog contains tracking information.

    Attributes:
        description: The description of the entire 3D box subcatalog.
        categories: All the possible categories in the corresponding dataset
            stored in a :class:`~graviti.utility.name.NameOrderedDict`
            with the category names as keys
            and the :class:`~graviti.label.supports.CategoryInfo` as values.
        category_delimiter: The delimiter in category values indicating parent-child relationship.
        attributes: All the possible attributes in the corresponding dataset
            stored in a :class:`~graviti.utility.name.NameOrderedDict`
            with the attribute names as keys
            and the :class:`~graviti.label.attribute.AttributeInfo` as values.
        is_tracking: Whether the Subcatalog contains tracking information.

    """

    def __init__(self, is_tracking: bool = False) -> None:
        SupportIsTracking.__init__(self, is_tracking)


@SubcatalogTypeRegister(LabelType.POLYGON2D)
class Polygon2DSubcatalog(  # pylint: disable=too-many-ancestors
    SubcatalogBase, SupportIsTracking, SupportCategories, SupportAttributes
):
    """This class defines the subcatalog for 2D polygon type of labels.

    Arguments:
        is_tracking: A boolean value indicates whether the corresponding
            subcatalog contains tracking information.

    Attributes:
        description: The description of the entire 2D polygon subcatalog.
        categories: All the possible categories in the corresponding dataset
            stored in a :class:`~graviti.utility.name.NameOrderedDict`
            with the category names as keys
            and the :class:`~graviti.label.supports.CategoryInfo` as values.
        category_delimiter: The delimiter in category values indicating parent-child relationship.
        attributes: All the possible attributes in the corresponding dataset
            stored in a :class:`~graviti.utility.name.NameOrderedDict`
            with the attribute names as keys
            and the :class:`~graviti.label.attribute.AttributeInfo` as values.
        is_tracking: Whether the Subcatalog contains tracking information.

    """

    def __init__(self, is_tracking: bool = False) -> None:
        SupportIsTracking.__init__(self, is_tracking)


@SubcatalogTypeRegister(LabelType.POLYLINE2D)
class Polyline2DSubcatalog(  # pylint: disable=too-many-ancestors
    SubcatalogBase, SupportIsTracking, SupportCategories, SupportAttributes
):
    """This class defines the subcatalog for 2D polyline type of labels.

    Arguments:
        is_tracking: A boolean value indicates whether the corresponding
            subcatalog contains tracking information.

    Attributes:
        description: The description of the entire 2D polyline subcatalog.
        categories: All the possible categories in the corresponding dataset
            stored in a :class:`~graviti.utility.name.NameOrderedDict`
            with the category names as keys
            and the :class:`~graviti.label.supports.CategoryInfo` as values.
        category_delimiter: The delimiter in category values indicating parent-child relationship.
        attributes: All the possible attributes in the corresponding dataset
            stored in a :class:`~graviti.utility.name.NameOrderedDict`
            with the attribute names as keys
            and the :class:`~graviti.label.attribute.AttributeInfo` as values.
        is_tracking: Whether the Subcatalog contains tracking information.

    """

    def __init__(self, is_tracking: bool = False) -> None:
        SupportIsTracking.__init__(self, is_tracking)


@SubcatalogTypeRegister(LabelType.KEYPOINTS2D)
class Keypoints2DSubcatalog(  # pylint: disable=too-many-ancestors
    SubcatalogBase, SupportIsTracking, SupportCategories, SupportAttributes
):
    """This class defines the subcatalog for 2D keypoints type of labels.

    Arguments:
        is_tracking: A boolean value indicates whether the corresponding
            subcatalog contains tracking information.

    Attributes:
        description: The description of the entire 2D keypoints subcatalog.
        categories: All the possible categories in the corresponding dataset
            stored in a :class:`~graviti.utility.name.NameOrderedDict`
            with the category names as keys
            and the :class:`~graviti.label.supports.CategoryInfo` as values.
        category_delimiter: The delimiter in category values indicating parent-child relationship.
        attributes: All the possible attributes in the corresponding dataset
            stored in a :class:`~graviti.utility.name.NameOrderedDict`
            with the attribute names as keys
            and the :class:`~graviti.label.attribute.AttributeInfo` as values.
        is_tracking: Whether the Subcatalog contains tracking information.

    """

    def __init__(self, is_tracking: bool = False) -> None:
        SupportIsTracking.__init__(self, is_tracking)
        self._keypoints: List[KeypointsInfo] = []

    def _loads(self, contents: Dict[str, Any]) -> None:
        super()._loads(contents)
        self._keypoints = []
        for keypoint in contents["keypoints"]:
            self._keypoints.append(KeypointsInfo.loads(keypoint))

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

    @property
    def keypoints(self) -> List[KeypointsInfo]:
        """Return the KeypointsInfo of the Subcatalog.

        Returns:
            A list of :class:`~graviti.label.supports.KeypointsInfo`.

        """
        return self._keypoints

    def dumps(self) -> Dict[str, Any]:
        """Dumps all the information of the keypoints into a dict.

        Returns:
            A dict containing all the information of this Keypoints2DSubcatalog.

        """
        contents: Dict[str, Any] = super().dumps()
        if self._keypoints:
            contents["keypoints"] = [keypoint.dumps() for keypoint in self._keypoints]
        return contents


@SubcatalogTypeRegister(LabelType.SENTENCE)
class SentenceSubcatalog(SubcatalogBase, SupportAttributes):
    """This class defines the subcatalog for audio transcripted sentence type of labels.

    Arguments:
        is_sample: A boolen value indicates whether time format is sample related.
        sample_rate: The number of samples of audio carried per second.
        lexicon: A list consists all of text and phone.

    Attributes:
        description: The description of the entire sentence subcatalog.
        is_sample: A boolen value indicates whether time format is sample related.
        sample_rate: The number of samples of audio carried per second.
        lexicon: A list consists all of text and phone.
        attributes: All the possible attributes in the corresponding dataset
            stored in a :class:`~graviti.utility.name.NameOrderedDict`
            with the attribute names as keys
            and the :class:`~graviti.label.attribute.AttributeInfo` as values.

    Raises:
        TypeError: When sample_rate is None and is_sample is True.

    """

    def __init__(
        self,
        is_sample: bool = False,
        sample_rate: Optional[int] = None,
        lexicon: Optional[List[List[str]]] = None,
    ) -> None:
        if is_sample and not sample_rate:
            raise TypeError(
                f"Require 'sample_rate' to init {self.__class__.__name__} when is_sample is True"
            )

        self.is_sample = is_sample
        if sample_rate:
            self.sample_rate = sample_rate
        if lexicon:
            self.lexicon = lexicon

    def _loads(self, contents: Dict[str, Any]) -> None:
        super()._loads(contents)
        self.is_sample = contents.get("isSample", False)

        if self.is_sample:
            self.sample_rate = contents["sampleRate"]

        lexicon = contents.get("lexicon")
        if lexicon:
            self.lexicon = lexicon
        if "lexicon" in contents:
            self.lexicon = contents["lexicon"]

    def dumps(self) -> Dict[str, Any]:
        """Dumps the information of this SentenceSubcatalog into a dict.

        Returns:
            A dict containing all information of this SentenceSubcatalog.

        """
        contents = super().dumps()

        if self.is_sample:
            contents["isSample"] = self.is_sample
            contents["sampleRate"] = self.sample_rate

        if hasattr(self, "lexicon"):
            contents["lexicon"] = self.lexicon

        return contents

    def append_lexicon(self, lexemes: List[str]) -> None:
        """Add lexemes to lexicon.

        Arguments:
            lexemes: A list consists of text and phone.

        """
        if hasattr(self, "lexicon"):
            self.lexicon.append(lexemes)
        else:
            self.lexicon = [lexemes]


Subcatalogs = Union[
    ClassificationSubcatalog,
    Box2DSubcatalog,
    Box3DSubcatalog,
    Polygon2DSubcatalog,
    Polyline2DSubcatalog,
    Keypoints2DSubcatalog,
    SentenceSubcatalog,
]
