#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""This file defines class CatagoryInfo, AttributeInfo and Subcatalog."""

from enum import Enum, auto
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, TypeVar, Union

from ..utility import NameMixin, NameOrderedDict, ReprMixin, ReprType, common_loads
from .attributes import AttributeInfo, Items, _ArgType, _EnumElementType


class CategoryInfo(NameMixin):
    """Information of a category, includes category name and description

    :param name: The name of the category
    :param description: The description of the category
    """

    _T = TypeVar("_T", bound="CategoryInfo")

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, str]) -> _T:
        """Load a CategoryInfo from a dict containing the category.

        :param contents: A dict containing the information of a CategoryInfo
        {
            "name": <str>
            "description": <str>
        }
        :return: The loaded CategoryInfo
        """
        return common_loads(cls, contents)


class VisibleType(Enum):
    """All the possible visible types of keypoints labels."""

    TERNARY = auto()
    BINARY = auto()


class KeypointsInfo(ReprMixin):
    """Information of a type of keypoints label.

    :param number: The number of keypoints
    :param names: All the names of keypoints
    :param skeleton: The skeleton of keypoints
    :param visible: The visible type of keypoints
    :param parent_categories: The parent categories of the keypoints
    :param description: The description of keypoints
    """

    _repr_type = ReprType.INSTANCE
    _repr_attrs = (
        "number",
        "names",
        "skeleton",
        "visible",
        "parent_categories",
    )
    _T = TypeVar("_T", bound="KeypointsInfo")
    description = ""

    def __init__(
        self,
        number: int,
        *,
        names: Optional[Iterable[str]] = None,
        skeleton: Optional[Iterable[Iterable[int]]] = None,
        visible: Optional[VisibleType] = None,
        parent_categories: Union[None, str, Iterable[str]] = None,
        description: Optional[str] = None,
    ):
        self._number = number
        if names:
            self.names = list(names)
        if skeleton:
            self.skeleton: List[Tuple[int, int]] = [
                tuple(line) for line in skeleton  # type: ignore[misc]
            ]
        if visible:
            self.visible = visible
        if description:
            self.description = description

        if not parent_categories:
            return

        if isinstance(parent_categories, str):
            self.parent_categories = [parent_categories]
        else:
            self.parent_categories = list(parent_categories)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Load a KeypointsInfo from a dict containing the information of the keypoints.

        :param contents: A dict contains all information of the KeypointsInfo
        :return: The loaded KeypointsInfo
        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:
        self._number = contents["number"]

        if "names" in contents:
            self.names = contents["names"]

        if "skeleton" in contents:
            self.skeleton = [tuple(line) for line in contents["skeleton"]]  # type: ignore[misc]

        if "visible" in contents:
            self.visible = VisibleType[contents["visible"]]

        if "parentCategories" in contents:
            self.parent_categories = contents["parentCategories"]

        if "description" in contents:
            self.description = contents["description"]

    @property
    def number(self) -> int:
        """Get the number of the keypoints.

        :return: The number of the keypoints
        """
        return self._number

    def dumps(self) -> Dict[str, Any]:
        """Dump all the keypoint information into a dictionary.

        :return: A dictionary contains all information of the keypoint
        """
        contents: Dict[str, Any] = {"number": self._number}

        if hasattr(self, "names"):
            contents["names"] = self.names

        if hasattr(self, "skeleton"):
            contents["skeleton"] = self.skeleton

        if hasattr(self, "visible"):
            contents["visible"] = self.visible.name

        if hasattr(self, "parent_categories"):
            contents["parentCategories"] = self.parent_categories

        if self.description:
            contents["description"] = self.description

        return contents


class Supports:  # pylint: disable=too-few-public-methods
    """The base class of different support classes for subcatalog."""

    def _loads(self: Any, contents: Dict[str, Any]) -> None:
        raise NotImplementedError

    def _dumps(self: Any) -> Dict[str, bool]:
        raise NotImplementedError


class SupportIsTracking(Supports):  # pylint: disable=too-few-public-methods
    """A class support isTracking of a subcatalog"""

    def __init__(self, is_tracking: bool = False) -> None:
        self.is_tracking = is_tracking

    def _loads(self, contents: Dict[str, Any]) -> None:
        self.is_tracking = contents.get("isTracking", False)

    def _dumps(self) -> Dict[str, bool]:
        return {"isTracking": self.is_tracking} if self.is_tracking else {}


class SupportCategories(Supports):  # pylint: disable=too-few-public-methods
    """A class support categories of a subcatalog"""

    category_delimiter: str
    categories: NameOrderedDict[CategoryInfo]

    def _loads(self, contents: Dict[str, Any]) -> None:
        if "categories" not in contents:
            return
        if "categoryDelimiter" in contents:
            self.category_delimiter = contents["categoryDelimiter"]

        self.categories = NameOrderedDict()
        for category in contents["categories"]:
            self.categories.append(CategoryInfo.loads(category))

    def _dumps(self) -> Dict[str, Any]:
        if not hasattr(self, "categories"):
            return {}

        contents: Dict[str, Any] = {
            "categories": [category.dumps() for category in self.categories.values()]
        }
        if hasattr(self, "category_delimiter"):
            contents["categoryDelimiter"] = self.category_delimiter
        return contents

    def add_category(self, name: str, description: Optional[str] = None) -> None:
        """Add a category to the Subcatalog

        :param name: The name of the category
        :param description: The description of the category
        """
        if hasattr(self, "categories"):
            self.categories = NameOrderedDict()

        self.categories.append(CategoryInfo(name, description))


class SupportAttributes(Supports):  # pylint: disable=too-few-public-methods
    """A class support attributes of a subcatalog"""

    attributes: NameOrderedDict[AttributeInfo]

    def _loads(self, contents: Dict[str, Any]) -> None:
        if "attributes" not in contents:
            return

        self.attributes = NameOrderedDict()
        for attribute in contents["attributes"]:
            self.attributes.append(AttributeInfo.loads(attribute))

    def _dumps(self) -> Dict[str, Any]:
        if hasattr(self, "attributes"):
            return {"attributes": [attribute.dumps() for attribute in self.attributes.values()]}
        return {}

    def add_attribute(
        self,
        name: str,
        *,
        type_: _ArgType = "",
        enum: Optional[Iterable[_EnumElementType]] = None,
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
        items: Optional[Items] = None,
        parent_categories: Union[None, str, Iterable[str]] = None,
        description: Optional[str] = None,
    ) -> None:
        """Add a attribute to the Subcatalog

        :param name: The name of the attribute
        enum: All the possible values of the attribute.
        type_: The type of the attribute value.
        minimum: The minimum value of number type attribute.
        maximum: The maximum value of number type attribute.
        items: The item inside array type attributes.
        :param parent_categories: The parent categories of the attribute
        :param description: The description of the attributes
        """
        attribute_info = AttributeInfo(
            name,
            type_=type_,
            enum=enum,
            minimum=minimum,
            maximum=maximum,
            items=items,
            parent_categories=parent_categories,
            description=description,
        )

        if hasattr(self, "attributes"):
            self.attributes = NameOrderedDict()

        self.attributes.append(attribute_info)
