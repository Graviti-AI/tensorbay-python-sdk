#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""CatagoryInfo, KeypointsInfo and different SubcatalogMixin classes.

:class:`CatagoryInfo` defines a category with the name and description of it.

:class:`KeypointsInfo` defines the structure of a set of keypoints.

:class:`SubcatalogMixin` is the base class of different mixin classes for subcatalog.

.. table:: mixin classes for subcatalog
   :widths: auto

   ============================  ===============================================================
   mixin classes for subcatalog  explaination
   ============================  ===============================================================
   :class:`IsTrackingMixin`      a mixin class supporting tracking information of a subcatalog
   :class:`CategoriesMixin`      a mixin class supporting category information of a subcatalog
   :class:`AttributesMixin`      a mixin class supporting attribute information of a subcatalog
   ============================  ===============================================================

"""

from enum import Enum, auto
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, TypeVar, Union

from ..utility import EqMixin, NameMixin, NameOrderedDict, ReprMixin, ReprType, common_loads
from .attributes import AttributeInfo, Items, _ArgType, _EnumElementType


class CategoryInfo(NameMixin):
    """This class represents the information of a category, including category name and description.

    Arguments:
        name: The name of the category.
        description: The description of the category.

    Attributes:
        name: The name of the category.
        description: The description of the category.

    Examples:
        >>> CategoryInfo(name="example", description="This is an example")
        CategoryInfo("example")

    """

    _T = TypeVar("_T", bound="CategoryInfo")

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, str]) -> _T:
        """Loads a CategoryInfo from a dict containing the category.

        Arguments:
            contents: A dict containing the information of the category.

        Returns:
            The loaded :class:`CategoryInfo` object.

        Examples:
            >>> contents = {"name": "example", "description": "This is an exmaple"}
            >>> CategoryInfo.loads(contents)
            CategoryInfo("example")

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, str]:
        """Dumps the CatagoryInfo into a dict.

        Returns:
            A dict containing the information in the CategoryInfo.

        Examples:
            >>> categoryinfo = CategoryInfo(name="example", description="This is an example")
            >>> categoryinfo.dumps()
            {'name': 'example', 'description': 'This is an example'}

        """
        return super()._dumps()


class _VisibleType(Enum):
    """All the possible visible types of keypoints labels."""

    TERNARY = auto()
    BINARY = auto()


class KeypointsInfo(ReprMixin, EqMixin):
    """This class defines the structure of a set of keypoints.

    Arguments:
        number: The number of the set of keypoints.
        names: All the names of the keypoints.
        skeleton: The skeleton of the keypoints
            indicating which keypoint should connect with another.
        visible: The visible type of the keypoints, can only be 'BINARY' or 'TERNARY'.
            It determines the range of the
            :attr:`Keypoint2D.v<tensorbay.geometry.keypoint.Keypoint2D.v>`.
        parent_categories: The parent categories of the keypoints.
        description: The description of the keypoints.

    Attributes:
        names: All the names of the keypoints.
        skeleton: The skeleton of the keypoints
            indicating which keypoint should connect with another.
        visible: The visible type of the keypoints, can only be 'BINARY' or 'TERNARY'.
            It determines the range of the
            :attr:`Keypoint2D.v<tensorbay.geometry.keypoint.Keypoint2D.v>`.
        parent_categories: The parent categories of the keypoints.
        description: The description of the keypoints.

    Examples:
        >>> KeypointsInfo(
        ...     2,
        ...     names=["L_Shoulder", "R_Shoulder"],
        ...     skeleton=[(0, 1)],
        ...     visible="BINARY",
        ...     parent_categories="people",
        ...     description="example",
        ... )
        KeypointsInfo(
          (number): 2,
          (names): [...],
          (skeleton): [...],
          (visible): 'BINARY',
          (parent_categories): [...]
        )

    """

    _T = TypeVar("_T", bound="KeypointsInfo")

    _repr_type = ReprType.INSTANCE
    _repr_attrs = (
        "number",
        "names",
        "skeleton",
        "visible",
        "parent_categories",
    )

    description = ""

    def __init__(
        self,
        number: int,
        *,
        names: Optional[Iterable[str]] = None,
        skeleton: Optional[Iterable[Iterable[int]]] = None,
        visible: Optional[str] = None,
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
            try:
                self.visible = _VisibleType[visible.upper()].name
            except KeyError as error:
                raise ValueError("Visible can only be 'BINARY' or 'TERNARY'") from error

        if description:
            self.description = description

        if not parent_categories:
            return

        if isinstance(parent_categories, str):
            self.parent_categories = [parent_categories]
        else:
            self.parent_categories = list(parent_categories)

    def _loads(self, contents: Dict[str, Any]) -> None:
        self._number = contents["number"]

        if "names" in contents:
            self.names = contents["names"]

        if "skeleton" in contents:
            self.skeleton = [tuple(line) for line in contents["skeleton"]]  # type: ignore[misc]

        if "visible" in contents:
            self.visible = _VisibleType[contents["visible"]].name

        if "parentCategories" in contents:
            self.parent_categories = contents["parentCategories"]

        if "description" in contents:
            self.description = contents["description"]

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a KeypointsInfo from a dict containing the information of the keypoints.

        Arguments:
            contents: A dict containing all the information of the set of keypoints.

        Returns:
            The loaded :class:`KeypointsInfo` object.

        Examples:
            >>> contents = {
            ...     "number": 2,
            ...     "names": ["L", "R"],
            ...     "skeleton": [(0,1)],
            ...     "visible": "TERNARY",
            ...     "parentCategories": ["example"],
            ...     "description": "example",
            ... }
            >>> KeypointsInfo.loads(contents)
            KeypointsInfo(
              (number): 2,
              (names): [...],
              (skeleton): [...],
              (visible): 'TERNARY',
              (parent_categories): [...]
            )

        """
        return common_loads(cls, contents)

    @property
    def number(self) -> int:
        """Return the number of the keypoints.

        Returns:
            The number of the keypoints.

        Examples:
            >>> keypointsinfo = KeypointsInfo(5)
            >>> keypointsinfo.number
            5

        """
        return self._number

    def dumps(self) -> Dict[str, Any]:
        """Dumps all the keypoint information into a dict.

        Returns:
            A dict containing all the information of the keypoint.

        Examples:
            >>> keypointsinfo = KeypointsInfo(
            ...     2,
            ...     names=["L_Shoulder", "R_Shoulder"],
            ...     skeleton=[(0, 1)],
            ...     visible="BINARY",
            ...     parent_categories="people",
            ...     description="example",
            ... )
            >>> keypointsinfo.dumps()
            {
                'number': 2,
                'names': ['L_Shoulder', 'R_Shoulder'],
                'skeleton': [(0, 1)],
                'visible': 'BINARY',
                'parentCategories': ['people'],
                'description': 'example',
            }

        """
        contents: Dict[str, Any] = {"number": self._number}

        if hasattr(self, "names"):
            contents["names"] = self.names

        if hasattr(self, "skeleton"):
            contents["skeleton"] = self.skeleton

        if hasattr(self, "visible"):
            contents["visible"] = self.visible

        if hasattr(self, "parent_categories"):
            contents["parentCategories"] = self.parent_categories

        if self.description:
            contents["description"] = self.description

        return contents


class SubcatalogMixin(EqMixin):  # pylint: disable=too-few-public-methods
    """The base class of different mixin classes for subcatalog."""

    def _loads(self: Any, contents: Dict[str, Any]) -> None:
        raise NotImplementedError

    def _dumps(self: Any) -> Dict[str, bool]:
        raise NotImplementedError


class IsTrackingMixin(SubcatalogMixin):  # pylint: disable=too-few-public-methods
    """A mixin class supporting tracking information of a subcatalog.

    Arguments:
        is_tracking: Whether the Subcatalog contains tracking information.

    Attributes:
        is_tracking: Whether the Subcatalog contains tracking information.

    """

    def __init__(self, is_tracking: bool = False) -> None:
        self.is_tracking = is_tracking

    def _loads(self, contents: Dict[str, Any]) -> None:
        self.is_tracking = contents.get("isTracking", False)

    def _dumps(self) -> Dict[str, bool]:
        return {"isTracking": self.is_tracking} if self.is_tracking else {}


class CategoriesMixin(SubcatalogMixin):  # pylint: disable=too-few-public-methods
    """A mixin class supporting category information of a subcatalog.

    Attributes:
        categories: All the possible categories in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameOrderedDict`
            with the category names as keys
            and the :class:`~tensorbay.label.supports.CategoryInfo` as values.
        category_delimiter: The delimiter in category values indicating parent-child relationship.

    """

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
        """Add a category to the Subcatalog.

        Arguments:
            name: The name of the category.
            description: The description of the category.

        """
        if not hasattr(self, "categories"):
            self.categories = NameOrderedDict()

        self.categories.append(CategoryInfo(name, description))


class AttributesMixin(SubcatalogMixin):  # pylint: disable=too-few-public-methods
    """A mixin class supporting attribute information of a subcatalog.

    Attributes:
        attributes: All the possible attributes in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameOrderedDict`
            with the attribute names as keys
            and the :class:`~tensorbay.label.attribute.AttributeInfo` as values.

    """

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
        """Add an attribute to the Subcatalog.

        Arguments:
            name: The name of the attribute.
            type_: The type of the attribute value, could be a single type or multi-types.
                The type must be within the followings:
                - array
                - boolean
                - integer
                - number
                - string
                - null
                - instance
            enum: All the possible values of an enumeration attribute.
            minimum: The minimum value of number type attribute.
            maximum: The maximum value of number type attribute.
            items: The items inside array type attributes.
            parent_categories: The parent categories of the attribute.
            description: The description of the attributes.

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

        if not hasattr(self, "attributes"):
            self.attributes = NameOrderedDict()

        self.attributes.append(attribute_info)
