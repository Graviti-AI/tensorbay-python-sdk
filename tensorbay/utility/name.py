#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""NameMixin, NameSortedDict, NameSortedList and NameOrderedDict.

:class:`NameMixin` is a mixin class for instance which has immutable name and mutable description.

:class:`NameSortedDict` is a sorted mapping class which contains :class:`NameMixin`.
The corrsponding key is the 'name' of :class:`NameMixin`.

:class:`NameSortedList` is a sorted sequence class which contains :class:`NameMixin`.
It is maintained in sorted order according to the 'name' of :class:`NameMixin`.

:class:`NameOrderedDict` is an ordered mapping class which contains :class:`NameMixin`.
The corrsponding key is the 'name' of :class:`NameMixin`.

"""

from collections import OrderedDict
from typing import Dict, Iterator, List, Mapping, Optional, Sequence, Type, TypeVar, Union, overload

from sortedcontainers import SortedDict

from ..utility import EqMixin, common_loads
from .repr import ReprMixin
from .user import UserMapping


class NameMixin(ReprMixin, EqMixin):
    """A mixin class for instance which has immutable name and mutable description.

    Arguments:
        name: Name of the class.
        description: Description of the class.

    """

    _P = TypeVar("_P", bound="NameMixin")

    description = ""

    def __init__(self, name: str, description: Optional[str] = None) -> None:
        self._name = name
        if description:
            self.description = description

    def _repr_head(self) -> str:
        return f'{self.__class__.__name__}("{self._name}")'

    def _loads(self, contents: Dict[str, str]) -> None:
        self._name = contents["name"]
        if "description" in contents:
            self.description = contents["description"]

    def _dumps(self) -> Dict[str, str]:
        """Dumps the instance into a dict.

        Returns:
            A dict containing the name and the description,
            whose format is like::

                {
                    "name": <str>
                    "description": <str>
                }

        """
        contents = {"name": self._name}
        if self.description:
            contents["description"] = self.description

        return contents

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


class NameOrderedDict(UserMapping[str, _T]):
    """Name ordered dict is an ordered mapping which contains NameMixin.

    The corrsponding key is the 'name' of :class:`NameMixin`.

    """

    def __init__(self) -> None:
        self._data: "OrderedDict[str, _T]" = OrderedDict()

    def append(self, value: _T) -> None:
        """Store element in ordered dict.

        Arguments:
            value: :class:`NameMixin` instance.

        """
        self._data[value.name] = value
