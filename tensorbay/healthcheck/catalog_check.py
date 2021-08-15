#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Method check_catalog.

:meth:`check_catalog` checks the catalog of :class:`~tensorbay.dataset.dataset.Dataset`
or :class:`~tensorbay.dataset.dataset.FusionDataset`,
including subcatalog, categories and attributes.
For :class:`~tensorbay.label.attributes.AttributeInfo`,
it finds errors in fields such as 'type', 'enum', 'range' and 'parent categories'.

"""

from typing import Iterator, Optional, Tuple

from ..label import AttributeInfo, Catalog, CategoryInfo
from ..utility import NameList
from .pipeline import PipelineForIterable
from .report import Error


class AttributeInfoError(Error):
    """This class defines :class:`AttributeInfoError`.

    Arguments:
        name: The name of the attribute which has error.

    """

    def __init__(self, name: str) -> None:
        self._name = name


ATTRIBUTE_INFO_PIPELINE: PipelineForIterable[
    AttributeInfo, AttributeInfoError
] = PipelineForIterable()


def check_catalog(catalog: Catalog) -> Iterator[Tuple[str, AttributeInfoError]]:
    """The health check method for :class:`~tensorbay.label.catalog.Catalog`.

    Arguments:
        catalog: The :class:`~tensorbay.label.catalog.Catalog` needs to be checked.

    Yields:
        The label type and :class:`AttributeInfoError` indicating that
        :class:`~tensorbay.label.attributes.AttributeInfo` has invalid 'type', 'enum', 'range'
        or 'parent categories' field.

    """
    for key in catalog._attrs_fields:  # pylint: disable=protected-access
        subcatalog = getattr(catalog, key, None)
        if not subcatalog:
            continue
        categories = getattr(subcatalog, "categories", None)
        if hasattr(subcatalog, "attributes"):
            attribute_info_pipeline = ATTRIBUTE_INFO_PIPELINE.copy()
            attribute_info_pipeline.register(CheckParentCategories(categories))
            for error in attribute_info_pipeline(subcatalog.attributes.values()):
                yield key, error


class InvalidTypeError(AttributeInfoError):
    """The health check class for invalid.

    This error is raised to indicate that
    :class:`~tensorbay.label.attributes.AttributeInfo` has invalid 'type' field.

    """

    def __str__(self) -> str:
        return f'AttributeInfo "{self._name}": "type" field is invalid'


@ATTRIBUTE_INFO_PIPELINE.register
def check_invalid_type(attribute_info: AttributeInfo) -> Iterator[InvalidTypeError]:
    """The health check method for invalid type.

    :class:`~tensorbay.label.attributes.AttributeInfo` 'type' field.

    Arguments:
        attribute_info: The :class:`~tensorbay.label.attributes.AttributeInfo` needs to be checked.

    Yields:
        :class:`InvalidTypeError` indicating that
        :class:`~tensorbay.label.attributes.AttributeInfo` has invalid 'type' field.

    """
    if not hasattr(attribute_info, "type"):
        return

    type_ = attribute_info.type

    if type_ == "null":
        yield InvalidTypeError(attribute_info.name)
        return

    if not isinstance(type_, list):
        return

    length = len(type_)
    if length in (0, 1):
        yield InvalidTypeError(attribute_info.name)
        return

    if len(set(type_)) != length:
        yield InvalidTypeError(attribute_info.name)


class InvalidEnumError(AttributeInfoError):
    """The health check class for invalid enum.

    This error is raised to indicate that
    :class:`~tensorbay.label.attributes.AttributeInfo` has invalid 'enum' field.

    """

    def __str__(self) -> str:
        return f'AttributeInfo "{self._name}": "enum" field is invalid'


@ATTRIBUTE_INFO_PIPELINE.register
def check_invalid_enum(attribute_info: AttributeInfo) -> Iterator[InvalidEnumError]:
    """The health check method for invalid enum.

    :class:`~tensorbay.label.attributes.AttributeInfo` 'enum' field.

    Arguments:
        attribute_info: The :class:`~tensorbay.label.attributes.AttributeInfo` needs to be checked.

    Yields:
        :class:`InvalidEnumError` indicating that
        :class:`~tensorbay.label.attributes.AttributeInfo` has invalid 'enum' field.

    """
    if not hasattr(attribute_info, "enum"):
        return

    enum = attribute_info.enum
    length = len(enum)
    if length in (0, 1):
        yield InvalidEnumError(attribute_info.name)
        return

    if len(set(enum)) != length:
        yield InvalidEnumError(attribute_info.name)


class NeitherTypeNorEnumError(AttributeInfoError):
    """The health check class for either type enum.

    This error is raised to indicate
    :class:`~tensorbay.label.attributes.AttributeInfo` has neither 'enum' nor 'type'.

    """

    def __str__(self) -> str:
        return f'AttributeInfo "{self._name}": Neither "type" nor "enum" field exists'


@ATTRIBUTE_INFO_PIPELINE.register
def check_neither_type_nor_enum(attribute_info: AttributeInfo) -> Iterator[NeitherTypeNorEnumError]:
    """The health check method for :class:`~tensorbay.label.attributes.AttributeInfo`.

    which has neither 'enum' nor 'type' field.

    Arguments:
        attribute_info: The :class:`~tensorbay.label.attributes.AttributeInfo` needs to be checked.

    Yields:
        :class:`NeitherTypeNorEnumError` indicating that
        :class:`~tensorbay.label.attributes.AttributeInfo` has neither 'enum' nor 'type' field.

    """
    if not hasattr(attribute_info, "enum") and not hasattr(attribute_info, "type"):
        yield NeitherTypeNorEnumError(attribute_info.name)


class RedundantTypeError(AttributeInfoError):
    """The health check class for redundant type error.

    This error is raised to indicate that
    :class:`~tensorbay.label.attributes.AttributeInfo` has both 'enum' and 'type'.

    """

    def __str__(self) -> str:
        return f'AttributeInfo "{self._name}": "type" field is redundant when "enum" field exists'


@ATTRIBUTE_INFO_PIPELINE.register
def check_redundant_type(attribute_info: AttributeInfo) -> Iterator[RedundantTypeError]:
    """The health check method for redundant type.

    :class:`~tensorbay.label.attributes.AttributeInfo`
    which has both 'enum' and 'type' field.

    Arguments:
        attribute_info: The :class:`~tensorbay.label.attributes.AttributeInfo` needs to be checked.

    Yields:
        :class:`RedundantTypeError` indicating that
        :class:`~tensorbay.label.attributes.AttributeInfo` has both 'enum' and 'type' field.

    """
    if hasattr(attribute_info, "enum") and hasattr(attribute_info, "type"):
        yield RedundantTypeError(attribute_info.name)


class RangeNotSupportError(AttributeInfoError):
    """The health check class for range not support error.

    This error is raised to indicate :class:`~tensorbay.label.attributes.AttributeInfo`
    has range for non number type.

    """

    def __str__(self) -> str:
        return f'AttributeInfo "{self._name}": Only "number" and "integer" type supports range'


@ATTRIBUTE_INFO_PIPELINE.register
def check_range_not_support(attribute_info: AttributeInfo) -> Iterator[RangeNotSupportError]:
    """The health check method for range not support.

    :class:`~tensorbay.label.attributes.AttributeInfo` which has range for non number type.

    Arguments:
        attribute_info: The :class:`~tensorbay.label.attributes.AttributeInfo` needs to be checked.

    Yields:
        :class:`RangeNotSupportError` indicating that
        :class:`~tensorbay.label.attributes.AttributeInfo` has range for non number type.

    """
    if not hasattr(attribute_info, "maximum") and not hasattr(attribute_info, "minimum"):
        return

    type_ = getattr(attribute_info, "type", None)
    if isinstance(type_, list):
        if "number" in type_:
            return

        if "integer" in type_:
            return

    elif type_ in ("number", "integer"):
        return

    yield RangeNotSupportError(attribute_info.name)


class InvalidRangeError(AttributeInfoError):
    """The health check class for invalid range error.

    This error is raised to indicate that
    :class:`~tensorbay.label.attributes.AttributeInfo` has invalid range.

    """

    def __str__(self) -> str:
        return f'AttributeInfo "{self._name}": Maximum is not larger than minimum'


@ATTRIBUTE_INFO_PIPELINE.register
def check_invalid_range(attribute_info: AttributeInfo) -> Iterator[InvalidRangeError]:
    """The health check method for invalid range.

    :class:`~tensorbay.label.attributes.AttributeInfo`
    which has invalid range.

    Arguments:
        attribute_info: The :class:`~tensorbay.label.attributes.AttributeInfo` needs to be checked.

    Yields:
        :class:`InvalidRangeError` indicating that
        :class:`~tensorbay.label.attributes.AttributeInfo` has invalid range.

    """
    if attribute_info.maximum is None or attribute_info.minimum is None:
        return

    if attribute_info.maximum > attribute_info.minimum:
        return

    yield InvalidRangeError(attribute_info.name)


class InvalidParentCategories(AttributeInfoError):
    """The health check class for invalid parent categories.

    This error is raised to indicate that :class:`~tensorbay.label.attributes.AttributeInfo`
    has invalid parent categories.This means the category in parent_categories
    cannot be found in Subcatalog.categories.

    Arguments:
        name: The name of the incorrect attribute.
        invalid_parent_category: The name of the incorrect parent_category.

    """

    def __init__(self, name: str, invalid_parent_category: str) -> None:
        super().__init__(name)
        self._invalid_parent_category = invalid_parent_category

    def __str__(self) -> str:
        return (
            f'AttributeInfo "{self._name}":'
            f'parent category "{self._invalid_parent_category}" is invalid'
        )


class CheckParentCategories:
    """The health check class for parent categories.

    This error is raised to indicate that :class:`~tensorbay.label.attributes.AttributeInfo`
    has invalid parent_categories.

    Arguments:
        categories: The dictionary of :class:`~tensorbay.label.supports.CategoryInfo`
            which indicates all valid parent categories.

    """

    def __init__(self, categories: Optional[NameList[CategoryInfo]]) -> None:
        self._keys = set(categories.keys()) if categories else set()

    def __call__(self, attribute_info: AttributeInfo) -> Iterator[InvalidParentCategories]:
        """The health check method for parent categories.

        :class:`~tensorbay.label.attributes.AttributeInfo`
        which has invalid parent categories.

        Arguments:
            attribute_info: :class:`~tensorbay.label.attributes.AttributeInfo` needs to be checked.

        Yields:
            :class:`InvalidParentCategories` indicating that
            :class:`~tensorbay.label.attributes.AttributeInfo` has invalid parent categories.

        """
        for parent_category in attribute_info.parent_categories:
            if parent_category not in self._keys:
                yield InvalidParentCategories(attribute_info.name, parent_category)
