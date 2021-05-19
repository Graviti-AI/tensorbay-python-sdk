#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""AttrsMixin and Field class.

:class:`AttrsMixin` provides a list of special methods based on field configs.

:class:`Field` is a class describing the attr related fields.

"""

from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar

from ..exception import AttrError

_T = TypeVar("_T")
_A = TypeVar("_A", bound="AttrsMixin")
_BUILTINS = {"builtins", None, "typing"}
_DEFAULT_ERROR_MESSAGE = "'{class_name}' object has no attribute '{attr_name}'"
_Callable = Callable[[Any], Any]


class Field:  # pylint: disable=too-few-public-methods
    """A class to identify attr fields.

    Arguments:
        is_dynamic: Whether attr is a dynamic attr.
        key: Display value of the attr.
        default: Default value of the attr.
        error_message: The custom error message of the attr.

    """

    # remove __slots__ and add __getattr__ due to: https://github.com/PyCQA/pylint/issues/4341
    # __slots__ = ("is_dynamic", "key", "default", "error_message", "loader", "dumper")

    def __init__(
        self, is_dynamic: bool, key: str, default: Any, error_message: Optional[str]
    ) -> None:
        self.loader: _Callable
        self.dumper: _Callable

        self.is_dynamic = is_dynamic
        self.key = key
        self.default = default

        if error_message:
            self.error_message = error_message

    def __getattr__(self, name: str) -> None:
        raise AttributeError(
            _DEFAULT_ERROR_MESSAGE.format(class_name=self.__class__.__name__, attr_name=name)
        )


class AttrsMixin:
    """AttrsMixin provides a list of special methods based on attr fields.

    Examples:
        box2d: Box2DSubcatalog = attr(is_dynamic=True, key="BOX2D")

    """

    _attrs_fields: Dict[str, Field]
    _attrs_supports: Set[Any]

    def __init_subclass__(cls) -> None:
        attrs_fields = {}

        for base_class in cls.__bases__:
            base_fields = getattr(base_class, "_attrs_fields", None)
            if base_fields:
                attrs_fields.update(base_fields)

        for name, type_ in getattr(cls, "__annotations__", {}).items():
            field = _get_field(cls, name, type_)
            if field:
                attrs_fields[name] = field

        cls._attrs_fields = attrs_fields
        cls._attrs_supports = set(getattr(cls, "_supports", ()))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self.__dict__ == other.__dict__

    def __getattr__(self, name: str) -> None:
        """Raise an AttributeError exception when an attr does not exist.

        Arguments:
            name: Name of the attr.

        Raises:
            AttributeError: When an attr does not exist.

        """
        error_message = getattr(
            self._attrs_fields.get(name), "error_message", _DEFAULT_ERROR_MESSAGE
        )
        raise AttributeError(
            error_message.format(class_name=self.__class__.__name__, attr_name=name)
        )

    def _loads(self, contents: Dict[str, Any]) -> None:
        """Load an instance from a dict containing the information of the contents.

        Arguments:
            contents: A dict containing all data.

        """
        for support in self._attrs_supports:
            support._loads(self, contents)  # pylint: disable=protected-access

        for name, field in self._attrs_fields.items():
            if field.is_dynamic and field.key not in contents:
                continue

            if field.default is not ...:
                value = contents.get(field.key, field.default)
            else:
                value = contents[field.key]

            setattr(self, name, field.loader(value))

    def _dumps(self) -> Dict[str, Any]:
        """Dumps all the information of attrs into a dict.

        Returns:
            contents: A dict containing all data of attrs.

        """
        contents: Dict[str, Any] = {}
        for support in getattr(self, "_supports", []):
            contents.update(support._dumps(self))  # pylint: disable=protected-access

        for name, field in self._attrs_fields.items():
            if field.is_dynamic and not hasattr(self, name):
                continue

            if field.default is not ...:
                value = getattr(self, name, field.default)
            else:
                value = getattr(self, name)

            contents[field.key] = field.dumper(value)
        return contents


def attr(
    *,
    is_dynamic: bool = False,
    key: str = "",
    default: Any = ...,
    error_message: Optional[str] = None,
) -> Any:
    """Return an instance to identify attr fields.

    Arguments:
        is_dynamic: Determine if this is a dynamic attr.
        key: Display value of the attr.
        default: Default value of the attr.
        error_message: The custom error message of the attr.

    Raises:
        AttrError: Dynamic attr cannot have default value.

    Returns:
        A :class:`Field` instance containing all attr fields.

    """
    if is_dynamic and default is not ...:
        raise AttrError()
    return Field(is_dynamic, key, default, error_message)


def _get_field(obj: _T, name: str, annotation: Any) -> Optional[Field]:
    field = getattr(obj, name, None)
    if not isinstance(field, Field):
        return None

    field.loader, field.dumper = _get_operators(annotation)
    if not field.key:
        field.key = name
    delattr(obj, name)

    return field


def _get_operators(annotation: Any, is_internal: bool = False) -> Tuple[_Callable, _Callable]:
    """Get attr operating methods by annotations.

     AttrsMixin has three operating types which are classified by attr annotation.
        1. builtin types, like str, int, None
        2. tensorbay custom class, like tensorbay.label.Classification
        3. tensorbay custom class list, like List[tensorbay.label.LabeledBox2D]

    Arguments:
        annotation: Type of the attr.
        is_internal: Whether the annotation is inside of typing.List.

    Returns:
        Operating methods of the annotation.

    """
    if getattr(annotation, "__origin__", None) == list:
        return _get_operators(annotation.__args__[0], True)

    if getattr(annotation, "__module__", None) in _BUILTINS:
        return _builtin_operator, _builtin_operator

    if not is_internal:
        return annotation.loads, _attr_dumper

    return lambda contents: [annotation.loads(content) for content in contents], _attr_list_dumper


def _builtin_operator(contents: _T) -> _T:
    return contents


def _attr_dumper(attr_: _A) -> Any:
    return attr_._dumps()  # pylint: disable=protected-access


def _attr_list_dumper(attrs: List[_A]) -> List[Any]:
    return [attr_._dumps() for attr_ in attrs]  # pylint: disable=protected-access
