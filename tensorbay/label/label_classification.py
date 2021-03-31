#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Classification.

:class:`ClassificationSubcatalog` defines the subcatalog for classification type of labels.

:class:`Classification` defines the concept of classification label,
which can apply to different types of data, such as images and texts.

"""

from typing import Any, Dict, Optional, Type, TypeVar

from ..utility import SubcatalogTypeRegister, TypeRegister, common_loads
from .basic import LabelType, SubcatalogBase, _LabelBase
from .supports import AttributesMixin, CategoriesMixin


@SubcatalogTypeRegister(LabelType.CLASSIFICATION)
class ClassificationSubcatalog(  # pylint: disable=too-many-ancestors
    SubcatalogBase, CategoriesMixin, AttributesMixin
):
    """This class defines the subcatalog for classification type of labels.

    Attributes:
        description: The description of the entire classification subcatalog.
        categories: All the possible categories in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameOrderedDict`
            with the category names as keys
            and the :class:`~tensorbay.label.supports.CategoryInfo` as values.
        category_delimiter: The delimiter in category values indicating parent-child relationship.
        attributes: All the possible attributes in the corresponding dataset
            stored in a :class:`~tensorbay.utility.name.NameOrderedDict`
            with the attribute names as keys
            and the :class:`~tensorbay.label.attribute.AttributeInfo` as values.

    Examples:
        *Initialization Method 1:* Init from ``ClassificationSubcatalog.loads()`` method.

        >>> catalog = {
        ...     "CLASSIFICATION": {
        ...         "categoryDelimiter": ".",
        ...         "categories": [
        ...             {"name": "a"},
        ...             {"name": "b"},
        ...         ],
        ...          "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        ...     }
        ... }
        >>> ClassificationSubcatalog.loads(catalog["CLASSIFICATION"])
        ClassificationSubcatalog(
          (category_delimiter): '.',
          (categories): NameOrderedDict {...},
          (attributes): NameOrderedDict {...}
        )

        *Initialization Method 2:* Init an empty ClassificationSubcatalog
        and then add the attributes.

        >>> from tensorbay.utility import NameOrderedDict
        >>> from tensorbay.label import CategoryInfo, AttributeInfo, KeypointsInfo
        >>> categories = NameOrderedDict()
        >>> categories.append(CategoryInfo("a"))
        >>> attributes = NameOrderedDict()
        >>> attributes.append(AttributeInfo("gender", enum=["female", "male"]))
        >>> classification_subcatalog = ClassificationSubcatalog()
        >>> classification_subcatalog.category_delimiter = "."
        >>> classification_subcatalog.categories = categories
        >>> classification_subcatalog.attributes = attributes
        >>> classification_subcatalog
        ClassificationSubcatalog(
          (category_delimiter): '.',
          (categories): NameOrderedDict {...},
          (attributes): NameOrderedDict {...}
        )

    """


@TypeRegister(LabelType.CLASSIFICATION)
class Classification(_LabelBase):
    """This class defines the concept of classification label.

    :class:`Classification` is the classification type of label,
    which applies to different types of data, such as images and texts.

    Arguments:
        category: The category of the label.
        attributes: The attributes of the label.

    Attributes:
        category: The category of the label.
        attributes: The attributes of the label.

    Examples:
        >>> Classification(category="example", attributes={"attr": "a"})
        Classification(
          (category): 'example',
          (attributes): {...}
        )

    """

    _T = TypeVar("_T", bound="Classification")

    _label_attrs = ("category", "attributes")

    _repr_attrs = _label_attrs

    def __init__(
        self,
        category: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        _LabelBase.__init__(self, category, attributes)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a Classification label from a dict containing the label information.

        Arguments:
            contents: A dict containing the information of the classification label.

        Returns:
            The loaded :class:`Classification` object.

        Examples:
            >>> contents = {"category": "example", "attributes": {"key": "value"}}
            >>> Classification.loads(contents)
            Classification(
              (category): 'example',
              (attributes): {...}
            )

        """
        return common_loads(cls, contents)
