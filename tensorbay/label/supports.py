#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""CatagoryInfo, MaskCategoryInfo, KeypointsInfo and different SubcatalogMixin classes.

:class:`CatagoryInfo` defines a category with the name and description of it.

:class:`MaskCategoryInfo` defines a category with the name, id and description of it.

:class:`KeypointsInfo` defines the structure of a set of keypoints.

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

from ..utility import (
    AttrsMixin,
    NameList,
    NameMixin,
    ReprMixin,
    ReprType,
    attr,
    camel,
    common_loads,
)
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
        return self._dumps()


class MaskCategoryInfo(CategoryInfo):
    """This class represents the information of a category, including name, id and description.

    Arguments:
        name: The name of the category.
        category_id: The id of the category.
        description: The description of the category.

    Attributes:
        name: The name of the category.
        category_id: The id of the category.
        description: The description of the category.

    Examples:
        >>> MaskCategoryInfo(name="example", category_id=1, description="This is an example")
        MaskCategoryInfo("example")(
          (category_id): 1
        )

    """

    _repr_attrs = ("category_id",)

    category_id: int = attr(key=camel)

    def __init__(self, name: str, category_id: int, description: str = "") -> None:
        super().__init__(name, description)
        self.category_id = category_id


class _VisibleType(Enum):
    """All the possible visible types of keypoints labels."""

    TERNARY = auto()
    BINARY = auto()


class KeypointsInfo(ReprMixin, AttrsMixin):
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
        number: The number of the set of keypoints.
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
    _number: int = attr(key="number")
    names: List[str] = attr(is_dynamic=True)
    skeleton: List[Tuple[int, int]] = attr(is_dynamic=True)
    visible: str = attr(is_dynamic=True)
    parent_categories: List[str] = attr(is_dynamic=True, key=camel)
    description: str = attr(default="")

    def __init__(
        self,
        number: int,
        *,
        names: Optional[Iterable[str]] = None,
        skeleton: Optional[Iterable[Iterable[int]]] = None,
        visible: Optional[str] = None,
        parent_categories: Union[None, str, Iterable[str]] = None,
        description: str = "",
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

        self.description = description

        if not parent_categories:
            return

        if isinstance(parent_categories, str):
            self.parent_categories = [parent_categories]
        else:
            self.parent_categories = list(parent_categories)

    def _loads(self, contents: Dict[str, Any]) -> None:
        if "visible" in contents:
            _ = _VisibleType[contents["visible"]]
        super()._loads(contents)

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
        return self._dumps()


class IsTrackingMixin(AttrsMixin):
    """A mixin class supporting tracking information of a subcatalog.

    Arguments:
        is_tracking: Whether the Subcatalog contains tracking information.

    Attributes:
        is_tracking: Whether the Subcatalog contains tracking information.

    """

    is_tracking: bool = attr(key=camel, default=False)

    def __init__(self, is_tracking: bool = False) -> None:
        self.is_tracking = is_tracking


class CategoriesMixin(AttrsMixin):
    """A mixin class supporting category information of a subcatalog.

    Attributes:
        categories: All the possible categories in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameList`
            with the category names as keys
            and the :class:`~tensorbay.label.supports.CategoryInfo` as values.
        category_delimiter: The delimiter in category values indicating parent-child relationship.

    """

    category_delimiter: str = attr(is_dynamic=True, key=camel)
    categories: NameList[CategoryInfo] = attr(is_dynamic=True)

    def get_category_to_index(self) -> Dict[str, int]:
        """Return the dict containing the conversion from category to index.

        Returns:
            A dict containing the conversion from category to index.

        """
        if not hasattr(self, "categories"):
            return {}

        return {category: index for index, category in enumerate(self.categories.keys())}

    def get_index_to_category(self) -> Dict[int, str]:
        """Return the dict containing the conversion from index to category.

        Returns:
            A dict containing the conversion from index to category.

        """
        if not hasattr(self, "categories"):
            return {}

        return dict(enumerate(self.categories.keys()))

    def add_category(self, name: str, description: str = "") -> None:
        """Add a category to the Subcatalog.

        Arguments:
            name: The name of the category.
            description: The description of the category.

        """
        if not hasattr(self, "categories"):
            self.categories = NameList()

        self.categories.append(CategoryInfo(name, description))


class MaskCategoriesMixin(AttrsMixin):
    """A mixin class supporting category information of a MaskSubcatalog.

    Attributes:
        categories: All the possible categories in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameList`
            with the category names as keys
            and the :class:`~tensorbay.label.supports.MaskCategoryInfo` as values.
        category_delimiter: The delimiter in category values indicating parent-child relationship.

    """

    category_delimiter: str = attr(is_dynamic=True, key=camel)
    categories: NameList[MaskCategoryInfo] = attr(is_dynamic=True)

    def get_category_to_index(self) -> Dict[str, int]:
        """Return the dict containing the conversion from category name to category id.

        Returns:
            A dict containing the conversion from category name to category id.

        """
        if not hasattr(self, "categories"):
            return {}

        return {item.name: item.category_id for item in self.categories}

    def get_index_to_category(self) -> Dict[int, str]:
        """Return the dict containing the conversion from category id to category name.

        Returns:
            A dict containing the conversion from category id to category name.

        """
        if not hasattr(self, "categories"):
            return {}

        return {item.category_id: item.name for item in self.categories}

    def add_category(self, name: str, category_id: int, description: str = "") -> None:
        """Add a category to the Subcatalog.

        Arguments:
            name: The name of the category.
            category_id: The id of the category.
            description: The description of the category.

        """
        if not hasattr(self, "categories"):
            self.categories = NameList()

        self.categories.append(MaskCategoryInfo(name, category_id, description))


class AttributesMixin(AttrsMixin):
    """A mixin class supporting attribute information of a subcatalog.

    Attributes:
        attributes: All the possible attributes in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameList`
            with the attribute names as keys
            and the :class:`~tensorbay.label.attribute.AttributeInfo` as values.

    """

    attributes: NameList[AttributeInfo] = attr(is_dynamic=True)

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
        description: str = "",
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
            self.attributes = NameList()

        self.attributes.append(attribute_info)
