#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""AttrsMixin and Field class.

:class:`AttrsMixin` provides a list of special methods based on field configs.

:class:`Field` is a class describing the attr related fields.

"""
from sys import version_info
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    no_type_check,
)

from typing_extensions import NoReturn, Protocol

from ..exception import AttrError

_T = TypeVar("_T")
_Callable = Callable[[Any], Any]
_KeyConverter = Callable[[str], str]
_BUILTINS = {"builtins", None, "typing"}
_DEFAULT_ERROR_MESSAGE = "'{class_name}' object has no attribute '{attr_name}'"
_ATTRS_BASE = "_attrs_base"


class _A(Protocol):
    def dumps(self) -> Any:
        """Dumps all the information of attrs into a dict."""


class Field:  # pylint: disable=too-many-instance-attributes
    """A class to identify attr fields.

    Arguments:
        is_dynamic: Whether attr is a dynamic attr.
        key: Display value of the attr in contents.
        default: Default value of the attr.
        error_message: The custom error message of the attr.
        loader: The custom loader of the attr.
        dumper: The custom dumper of the attr.

    """

    # remove __slots__ and add __getattr__ due to: https://github.com/PyCQA/pylint/issues/4341
    # __slots__ = ("is_dynamic", "key", "default", "error_message", "loader", "dumper")

    def __init__(
        self,
        *,
        is_dynamic: bool,
        key: Union[str, None, _KeyConverter],
        default: Any,
        error_message: Optional[str],
        loader: Optional[_Callable],
        dumper: Optional[_Callable],
    ) -> None:
        if loader:
            self.loader = loader

        if dumper:
            self.dumper = dumper

        self.is_dynamic = is_dynamic
        self.default = default

        if callable(key):
            self.key_converter = key
        else:
            self.key = key

        if error_message:
            self.error_message = error_message

    def __getattr__(self, name: str) -> NoReturn:
        raise AttributeError(
            _DEFAULT_ERROR_MESSAGE.format(class_name=self.__class__.__name__, attr_name=name)
        )


class BaseField:
    """A class to identify fields of base class.

    Arguments:
        key: Display value of the attr.

    """

    def __init__(self, key: Optional[str]) -> None:
        self.loader: _Callable
        self.dumper: _Callable
        self.key = key


class AttrsMixin:
    """AttrsMixin provides a list of special methods based on attr fields.

    Examples:
        box2d: Box2DSubcatalog = attr(is_dynamic=True, key="BOX2D")

    """

    _attrs_fields: Dict[str, Field]
    _attrs_base: Any

    def __init_subclass__(cls) -> None:
        type_ = cls.__annotations__.pop(_ATTRS_BASE, None)
        if type_:
            cls._attrs_base.loader = type_._loads  # pylint: disable=protected-access
            cls._attrs_base.dumper = getattr(type_, "_dumps", type_.dumps)

        attrs_fields = {}
        for base_class in cls.__bases__:
            base_fields = getattr(base_class, "_attrs_fields", None)
            if base_fields:
                attrs_fields.update(base_fields)
        for name, type_ in getattr(cls, "__annotations__", {}).items():
            field = getattr(cls, name, None)
            if isinstance(field, Field):
                need_loader = not hasattr(field, "loader")
                need_dumper = not hasattr(field, "dumper")
                if need_loader or need_dumper:
                    loader, dumper = _get_operators(type_)
                    if need_loader:
                        field.loader = loader
                    if need_dumper:
                        field.dumper = dumper

                if hasattr(field, "key_converter"):
                    field.key = field.key_converter(name)
                attrs_fields[name] = field
                delattr(cls, name)
        cls._attrs_fields = attrs_fields

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self.__dict__ == other.__dict__

    @no_type_check
    def __getattr__(self, name: str) -> NoReturn:
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

    def _loads(self, contents: Any) -> None:
        """Load an instance from a dict containing the information of the contents.

        Arguments:
            contents: A dict containing all data.

        """
        base = getattr(self, _ATTRS_BASE, None)
        if base:
            value = contents if base.key is None else contents[base.key]
            base.loader(self, value)

        for name, field in self._attrs_fields.items():
            if field.is_dynamic and field.key not in contents:
                continue

            if field.key is None:
                value = contents
            elif field.default is not ...:
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
        base = getattr(self, _ATTRS_BASE, None)
        if base:
            _key_dumper(base.key, contents, base.dumper(self))

        for name, field in self._attrs_fields.items():
            if field.is_dynamic and not hasattr(self, name):
                continue

            value = getattr(self, name)
            if value == field.default:
                continue

            _key_dumper(field.key, contents, field.dumper(value))
        return contents


def attr(
    *,
    is_dynamic: bool = False,
    key: Union[str, None, _KeyConverter] = lambda x: x,
    default: Any = ...,
    error_message: Optional[str] = None,
    loader: Optional[Callable[[Any], Any]] = None,
    dumper: Optional[Callable[[Any], Any]] = None,
) -> Any:
    """Return an instance to identify attr fields.

    Arguments:
        is_dynamic: Determine if this is a dynamic attr.
        key: Display value of the attr in contents.
        default: Default value of the attr.
        error_message: The custom error message of the attr.
        loader: The custom loader of the attr.
        dumper: The custom dumper of the attr.

    Raises:
        AttrError: Dynamic attr cannot have default value.

    Returns:
        A :class:`Field` instance containing all attr fields.

    """
    if is_dynamic and default is not ...:
        raise AttrError()

    return Field(
        is_dynamic=is_dynamic,
        key=key,
        default=default,
        error_message=error_message,
        loader=loader,
        dumper=dumper,
    )


def attr_base(key: Optional[str] = None) -> Any:
    """Return an instance to identify base class fields.

    Arguments:
        key: Display value of the attr.

    Returns:
        A :class:`BaseField` instance containing all base class fields.

    """
    return BaseField(key)


def upper(name: str) -> str:
    """Convert the name value to uppercase.

    Arguments:
        name: name of the attr.

    Returns:
        The uppercase value.
    """
    return name.upper()


def camel(name: str) -> str:
    """Convert the name value to camelcase.

    Arguments:
        name: name of the attr.

    Returns:
        The camelcase value.

    """
    mixed = name.title().replace("_", "")
    return f"{mixed[0].lower()}{mixed[1:]}"


def _key_dumper(key: Optional[str], contents: Dict[str, Any], value: Any) -> None:
    if key is None:
        contents.update(value)
    else:
        contents[key] = value


def _get_origin_in_3_7(annotation: Any) -> Any:
    return getattr(annotation, "__origin__", None)


def _get_origin_in_3_6(annotation: Any) -> Any:
    module = getattr(annotation, "__module__", None)
    if module in _BUILTINS:
        extra = getattr(annotation, "__extra__", None)
        if extra is not None:
            return extra

    return getattr(annotation, "__origin__", None)


_get_origin = _get_origin_in_3_6 if version_info < (3, 7) else _get_origin_in_3_7


def _get_operators(annotation: Any) -> Tuple[_Callable, _Callable]:
    """Get attr operating methods by annotations.

     AttrsMixin has three operating types which are classified by attr annotation.
        1. builtin types, like str, int, None
        2. tensorbay custom class, like tensorbay.label.Classification
        3. tensorbay custom class list or NameList, like List[tensorbay.label.LabeledBox2D]

    Arguments:
        annotation: Type of the attr.

    Returns:
        Operating methods of the annotation.

    """
    origin: Any = _get_origin(annotation)
    annotation_args = getattr(annotation, "__args__", ())
    if isinstance(origin, type) and issubclass(origin, Sequence):
        type_ = annotation_args[0]
    elif origin is Union and len(annotation_args) == 2 and type(None) in annotation_args:
        type_ = annotation_args[0] if isinstance(None, annotation_args[1]) else annotation_args[1]
    else:
        origin = None
        type_ = annotation

    if {getattr(origin, "__module__", None), getattr(type_, "__module__", None)} < _BUILTINS:
        return _builtin_operator, _builtin_operator

    if origin is None:
        return type_.loads, _attr_dumper

    if origin is Union:
        return (
            lambda contents: type_.loads(contents) if contents is not None else None,
            _attr_optional_dumper,
        )

    return (
        lambda contents: origin(type_.loads(content) for content in contents),
        _attr_list_dumper,
    )


def _builtin_operator(contents: _T) -> _T:
    return contents


def _attr_dumper(attr_: _A) -> Any:
    return attr_.dumps()


def _attr_optional_dumper(attr_: Optional[_A]) -> Any:
    if attr_ is not None:
        return attr_.dumps()
    return None


def _attr_list_dumper(attrs: List[_A]) -> List[Any]:
    return [attr_.dumps() for attr_ in attrs]
