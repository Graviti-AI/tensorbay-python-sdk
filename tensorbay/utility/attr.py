#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""dynamic_attr decorated and Field class.

:class:`AttrMixin` provides a list of special methods based field configs.

:class:`Field` is a object describe each defined field.

"""

from collections import OrderedDict, namedtuple
from typing import Any, Dict, Optional, Tuple, TypeVar

_T = TypeVar("_T")
OperateMethod = namedtuple("OperateMethod", ["loads", "dumps"])
BUILEINS_MAP = {"builtins": True, None: True, "List": False}


class Field:  # pylint: disable=too-few-public-methods
    """Return an object to identify dynamic_attr fields.

    Arguments:
        error_message: The custom error message of the attribute.
        is_dynamic: Determine if this is a dynamic attribute.
        content_key: Display value of the attribute.
        default: Default value of the attribute.
        method: A method to load contents in to attribute or dumps contents from attribute.

    Examples:
        self._dynamic_attr_fields =
            OrderedDict(
                "_name": Field(is_dynamic=False, content_key="name"),
                "classification": Field(content_key="CLASSIFICATION")
                "box2d": Field(content_key="BOX2D",
            )
    """

    __slots__ = (
        "_error_message",
        "_is_dynamic",
        "_content_key",
        "_default",
    )

    def __init__(  # pylint: disable=too-many-arguments
        self,
        error_message: Optional[str] = None,
        is_dynamic: bool = True,
        content_key: Optional[str] = None,
        default: Optional[str] = None,
    ) -> None:
        self._error_message = error_message
        self._is_dynamic = is_dynamic
        self._content_key = content_key
        self._default = default


class AttrMixin:
    """AttrMixin provides a list of special methods based field configs."""

    _dynamic_attr_fields: "OrderedDict[str, Field]" = OrderedDict()
    _attribute_with_opreate: Dict[str, OperateMethod] = {}

    def __init_subclass__(cls) -> None:
        cls_annotations = getattr(cls, "__annotations__", {})
        for attribute in cls._dynamic_attr_fields:
            cls._attribute_with_opreate[attribute] = _get_operate_type(
                cls_annotations.get(attribute)
            )

    def __eq__(self, other: object) -> bool:
        """This method defined here compares all the instance variables.

        Arguments:
            other: The other class of the object to be compare.

        Returns:
            Is compared.
        """
        if not isinstance(other, self.__class__):
            return False

        return self.__dict__ == other.__dict__

    def __getattr__(self, attr: str) -> None:
        """Raise an AttributeError exception when an attribute not founded in the usual places.

        Arguments:
            attr: Name of the attribute.

        Raises:
            AttributeError: custom error message.
        """
        error_message = getattr(self._dynamic_attr_fields.get(attr), "_error_message", None)
        if error_message is None:
            raise AttributeError(f"'{type(self).__name__}' object not support attribute '{attr}'")
        raise AttributeError(error_message)

    def _loads(self, contents: Dict[str, Any]) -> None:
        """Load a class from a dict.

        Arguments:
            contents: A dict containing all data.
        """
        for support in getattr(self, "_supports", []):
            support._loads(self, contents)  # pylint: disable=protected-access

        for attribute, field in self._dynamic_attr_fields.items():

            # pylint: disable=assignment-from-no-return
            need_setattr, attribute_value = _single_loads(
                attribute, field, contents, self._attribute_with_opreate[attribute]
            )
            if need_setattr:
                setattr(self, attribute, attribute_value)

    def _dumps(self) -> Dict[str, Any]:
        """Dumps the class to a dict.

        Returns:
            contents: A dict containing all data of the class
        """
        contents: Dict[str, Any] = {}
        for support in getattr(self, "_supports", []):
            contents.update(support._dumps(self))  # pylint: disable=protected-access

        for attribute, field in self._dynamic_attr_fields.items():
            contents.update(
                _single_dumps(self, attribute, field, self._attribute_with_opreate[attribute])
            )

        return contents


def _get_operate_type(annotation: Any, is_typing_list: bool = False) -> OperateMethod:
    """Convert attribute operate method from annotations.

     AttrMixin has three operate types which is classified by attribute annotation.
        1. builtins operate, like str, int
        2. tensorbay custom class, like Tensorbay.label.Classification
        3. tensorbay custom class list, like [Tensorbay.label.LabeledBox2D]

    Arguments:
        annotation: Type of the attribute.
        is_typing_list: Whether the annotation is typing.List.

    Returns:
        operate methods of the annotation
    """
    typing_name = getattr(annotation, "_name", None)
    module = typing_name if typing_name else getattr(annotation, "__module__", None)
    try:
        if BUILEINS_MAP[module]:
            return OperateMethod(lambda contents: contents, lambda attribute: attribute)
        return _get_operate_type(annotation.__args__[0], True)
    except KeyError:
        if is_typing_list:
            return OperateMethod(
                lambda contents: [annotation.load(content) for content in contents],
                lambda attribute: [attr.dumps() for attr in attribute],
            )
        return OperateMethod(
            lambda contents: annotation.load(contents),  # pylint: disable=unnecessary-lambda
            lambda attribute: attribute.dumps(),
        )


def _single_loads(
    attribute: str,  # pylint: disable=unused-argument
    field: Field,  # pylint: disable=unused-argument
    contents: Dict[str, Any],  # pylint: disable=unused-argument
    operate_method: OperateMethod,  # pylint: disable=unused-argument
) -> Tuple[bool, Any]:
    """A method to load contents in to attribute.

    Arguments:
        attribute: name of the attribute.
        field: an object contain all attribute related message.
        contents: A dict containing all data of the class.
        operate_method: Indicate how to loads contents into attribute.

    # noqa: DAR202, DAR102
    Returns:
        need_setattr: Whether attribute should to be set.
        attribute_value: The value of the attribute.
    """


def _single_dumps(
    obj: Any,  # pylint: disable=unused-argument
    attribute: str,  # pylint: disable=unused-argument
    field: Field,  # pylint: disable=unused-argument
    operate_method: OperateMethod,  # pylint: disable=unused-argument
) -> Any:
    """A method to dumps contents from attribute.

    Arguments:
        obj: The object need to be dumps.
        attribute: name of the attribute.
        field: an object contain all attribute related message.
        operate_method: Indicate how to dumps contents from attribute.

    # noqa: DAR202, DAR102
    Returns:
        contents: A dict containing all data of the attribute.
    """


def error_message_attribute(class_name: str) -> str:  # pylint: disable=unused-argument
    """Customized error message for `ErrorMessageType.ATTRIBUTE`.

    Arguments:
        class_name: The object name.

    Returns:
        The customized error message. # noqa: DAR202
    """
