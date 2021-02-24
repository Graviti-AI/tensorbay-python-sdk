#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#

"""This file defines class Subcatalogbase and Subcatalog classes for every LabelType."""

from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, TypeVar, Union

from ..utility import ReprMixin, ReprType, SubcatalogTypeRegister, TypeMixin, common_loads
from .label import LabelType
from .supports import (
    KeypointsInfo,
    SupportAttributes,
    SupportCategories,
    SupportIsTracking,
    Supports,
    VisibleType,
)

_T = TypeVar("_T", bound="SubcatalogBase")


class SubcatalogBase(TypeMixin[LabelType], ReprMixin):
    """A base class for subcatalog."""

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
        """Load a subcatalog from a dict containing the attributes of the subcatalog.

        :param contents: A dict contains description of the subcatalog
        :return: The loaded subcatalog
        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:
        if "description" in contents:
            self.description = contents["description"]
        for support in self._supports:
            support._loads(self, contents)  # pylint: disable=protected-access

    def dumps(self) -> Dict[str, Any]:
        """Dumps all the information of the subcatalog into a dict.

        :return: A dict containing all the information of the subcatalog
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
    """A subcatalog contains all labels in CLASSIFICATION type."""


@SubcatalogTypeRegister(LabelType.BOX2D)
class Box2DSubcatalog(  # pylint: disable=too-many-ancestors
    SubcatalogBase, SupportIsTracking, SupportCategories, SupportAttributes
):
    """A subcatalog contains all labels in Box2D type

    :param is_tracking: A boolean value indicates whether corresponding
        subcatalog is tracking related
    """

    def __init__(self, is_tracking: bool = False) -> None:
        SupportIsTracking.__init__(self, is_tracking)


@SubcatalogTypeRegister(LabelType.BOX3D)
class Box3DSubcatalog(  # pylint: disable=too-many-ancestors
    SubcatalogBase, SupportIsTracking, SupportCategories, SupportAttributes
):
    """A subcatalog contains all labels in Box3D type

    :param is_tracking: A boolean value indicates whether corresponding
        subcatalog is tracking related
    """

    def __init__(self, is_tracking: bool = False) -> None:
        SupportIsTracking.__init__(self, is_tracking)


@SubcatalogTypeRegister(LabelType.POLYGON2D)
class Polygon2DSubcatalog(  # pylint: disable=too-many-ancestors
    SubcatalogBase, SupportIsTracking, SupportCategories, SupportAttributes
):
    """A subcatalog contains all labels in Polygon2D type

    :param is_tracking: A boolean value indicates whether corresponding
        subcatalog is tracking related
    """

    def __init__(self, is_tracking: bool = False) -> None:
        SupportIsTracking.__init__(self, is_tracking)


@SubcatalogTypeRegister(LabelType.POLYLINE2D)
class Polyline2DSubcatalog(  # pylint: disable=too-many-ancestors
    SubcatalogBase, SupportIsTracking, SupportCategories, SupportAttributes
):
    """A subcatalog contains all labels in Polyline2D type

    :param is_tracking: A boolean value indicates whether corresponding
        subcatalog is tracking related
    """

    def __init__(self, is_tracking: bool = False) -> None:
        SupportIsTracking.__init__(self, is_tracking)


@SubcatalogTypeRegister(LabelType.KEYPOINTS2D)
class Keypoints2DSubcatalog(  # pylint: disable=too-many-ancestors
    SubcatalogBase, SupportIsTracking, SupportCategories, SupportAttributes
):
    """A subcatalog contains all keypoints labels.

    :param is_tracking: A boolean value indicates whether corresponding
        subcatalog is tracking related
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
        visible: Optional[VisibleType] = None,
        parent_categories: Union[None, str, Iterable[str]] = None,
        description: Optional[str] = None,
    ) -> None:
        """Add a type of keypoints to the subcatalog.

        :param number: The number of keypoints
        :param names: All the names of keypoints
        :param skeleton: The skeleton of keypoints
        :param visible: The visible type of keypoints
        :param parent_categories: The parent categories of the keypoints
        :param description: The description of keypoints
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
        """Get the KeypointsInfo of the Subcatalog.

        :return: A list of KeypointsInfo
        """
        return self._keypoints

    def dumps(self) -> Dict[str, Any]:
        """Dumps all the information of the keypoints into a dictionary

        :return: A dictionary contains all the information of this Keypoints2DSubcatalog
        """
        contents: Dict[str, Any] = super().dumps()
        if self._keypoints:
            contents["keypoints"] = [keypoint.dumps() for keypoint in self._keypoints]
        return contents


@SubcatalogTypeRegister(LabelType.SENTENCE)
class SentenceSubcatalog(SubcatalogBase, SupportAttributes):
    """A class representing audio subcatalog.

    :param is_sample: A boolen value indicates whether time format is sample related
    :param sample_rate: The number of samples of audio carried per second
    :param lexicon: A list consists all of text and phone
    :raises TypeError: When is_sample is True, sample_rate is required
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
        """Dumps the information of this SentenceSubcatalog into a dictionary.

        :return: A dictionary contains all information of this AudioSubCatalog
        """
        contents = super().dumps()

        if self.is_sample:
            contents["isSample"] = self.is_sample
            contents["sampleRate"] = self.sample_rate

        if hasattr(self, "lexicon"):
            contents["lexicon"] = self.lexicon

        return contents

    def append_lexicon(self, lexemes: List[str]) -> None:
        """Add lexemes to lexicon

        :param: A list consists of text and phone
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
