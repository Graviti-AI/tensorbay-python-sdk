#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""NameMixin, NameSortedDict, NameSortedList and NamedList.

:class:`NameMixin` is a mixin class for instance which has immutable name and mutable description.

:class:`NameSortedDict` is a sorted mapping class which contains :class:`NameMixin`.
The corrsponding key is the 'name' of :class:`NameMixin`.

:class:`NameSortedList` is a sorted sequence class which contains :class:`NameMixin`.
It is maintained in sorted order according to the 'name' of :class:`NameMixin`.

:class:`NamedList` is a list of named elements, supports searching the element by its name.

"""

from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from sortedcontainers import SortedDict

from .attr import AttrsMixin, attr
from .common import common_loads
from .repr import ReprMixin
from .user import UserMapping, UserSequence


class NameMixin(AttrsMixin, ReprMixin):
    """A mixin class for instance which has immutable name and mutable description.

    Arguments:
        name: Name of the class.
        description: Description of the class.

    Attributes:
        name: Name of the class.

    """

    _P = TypeVar("_P", bound="NameMixin")

    _name: str = attr(key="name")
    description: str = attr(default="")

    def __init__(self, name: str, description: str = "") -> None:
        self._name = name
        self.description = description

    def _repr_head(self) -> str:
        return f'{self.__class__.__name__}("{self._name}")'

    def dumps(self) -> Dict[str, str]:
        """Dumps the instance into a dict.

        Returns:
            A dict containing the name and the description,
            whose format is like::

                {
                    "name": <str>
                    "description": <str>
                }

        """
        return self._dumps()

    @classmethod
    def loads(cls: Type[_P], contents: Dict[str, str]) -> _P:
        """Loads a NameMixin from a dict containing the information of the NameMixin.

        Arguments:
            contents: A dict containing the information of the :class:`NameMixin`::

                    {
                        "name": <str>
                        "description": <str>
                    }

        Returns:
            A :class:`NameMixin` instance containing the information from the contents dict.

        """
        return common_loads(cls, contents)

    @property
    def name(self) -> str:
        """Return name of the instance.

        Returns:
            Name of the instance.

        """
        return self._name


_T = TypeVar("_T", bound=NameMixin)


class NameSortedDict(UserMapping[str, _T]):
    """Name sorted dict keys are maintained in sorted order.

    Name sorted dict is a sorted mapping which contains :class:`NameMixin`.
    The corrsponding key is the 'name' of :class:`NameMixin`.

    Arguments:
        data: A mapping from str to :class:`NameMixin` which needs to be
            transferred to :class:`NameSortedDict`.

    """

    def __init__(self, data: Optional[Mapping[str, _T]] = None) -> None:
        self._data: SortedDict = SortedDict(data)

    def add(self, value: _T) -> None:
        """Store element in name sorted dict.

        Arguments:
            value: :class:`NameMixin` instance.

        """
        self._data[value.name] = value


class NameSortedList(Sequence[_T]):  # pylint: disable=too-many-ancestors
    """Name sorted list is a sorted sequence which contains NameMixin.

    It is maintained in sorted order according to the 'name' of :class:`NameMixin`.

    """

    def __init__(self) -> None:
        self._data = SortedDict()

    def __len__(self) -> int:
        return self._data.__len__()  # type: ignore[no-any-return]

    @overload
    def __getitem__(self, index: int) -> _T:
        ...

    @overload
    def __getitem__(self, index: slice) -> List[_T]:
        ...

    def __getitem__(self, index: Union[int, slice]) -> Union[_T, List[_T]]:
        return self._data.values()[index]  # type: ignore[no-any-return]

    def __iter__(self) -> Iterator[_T]:
        return self._data.values().__iter__()  # type: ignore[no-any-return]

    def add(self, value: _T) -> None:
        """Store element in name sorted list.

        Arguments:
            value: :class:`NameMixin` instance.

        """
        self._data[value.name] = value

    def get_from_name(self, name: str) -> _T:
        """Get element in name sorted list from name of NameMixin.

        Arguments:
            name: Name of :class:`NameMixin` instance.

        Returns:
            The element to be get.

        """
        return self._data[name]  # type: ignore[no-any-return]


class NamedList(UserSequence[_T]):
    """NamedList is a list of named elements, supports searching the element by its name."""

    def __init__(self, values: Iterable[_T] = ()) -> None:
        self._data: List[_T] = []
        self._mapping: Dict[str, _T] = {}

        for value in values:
            self.append(value)

    @overload
    def __getitem__(self, index: Union[int, str]) -> _T:
        ...

    @overload
    def __getitem__(self, index: slice) -> List[_T]:
        ...

    def __getitem__(self, index: Union[int, str, slice]) -> Union[_T, List[_T]]:
        if isinstance(index, str):
            return self._mapping.__getitem__(index)

        return self._data.__getitem__(index)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self._data.__eq__(other._data)

    def keys(self) -> Tuple[str, ...]:
        """Get all element names.

        Returns:
            A tuple containing all elements names.

        """
        return tuple(item.name for item in self._data)

    def append(self, value: _T) -> None:
        """Append element to the end of the NamedList.

        Arguments:
            value: Element to be appended to the NamedList.

        Raises:
            KeyError: When the name of the appending object already exists in the NamedList.

        """
        if value.name in self._mapping:
            raise KeyError(f'name "{value.name}" is duplicated')

        self._data.append(value)
        self._mapping[value.name] = value
