#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Notes, DatasetBase, Dataset and FusionDataset.

:class:`Notes` contains the basic information of a :class:`DatasetBase`.

:class:`DatasetBase` defines the basic concept of a dataset,
which is the top-level structure to handle your data files, labels and other additional information.

It represents a whole dataset contains several segments
and is the base class of :class:`Dataset` and :class:`FusionDataset`.

:class:`Dataset` is made up of data collected from only one sensor
or data without sensor information.
It consists of a list of :class:`~tensorbay.dataset.segment.Segment`.

:class:`FusionDataset` is made up of data collected from multiple sensors.
It consists of a list of :class:`~tensorbay.dataset.segment.FusionSegment`.

"""

import json
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    KeysView,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from ..label import Catalog
from ..utility import (
    AttrsMixin,
    NameMixin,
    ReprMixin,
    ReprType,
    SortedNameList,
    attr,
    camel,
    common_loads,
    locked,
)
from .segment import FusionSegment, Segment

if TYPE_CHECKING:
    from ..client import GAS

_T = TypeVar("_T", FusionSegment, Segment)


class Notes(AttrsMixin, ReprMixin):
    """This is a class stores the basic information of :class:`DatasetBase`.

    Arguments:
        is_continuous: Whether the data inside the dataset is time-continuous.
        bin_point_cloud_fields: The field names of the bin point cloud files in the dataset.

    """

    _T = TypeVar("_T", bound="Notes")

    _repr_attrs = ("is_continuous", "bin_point_cloud_fields")

    is_continuous: bool = attr(key=camel, default=False)
    bin_point_cloud_fields: Optional[List[str]] = attr(key=camel, default=None)

    def __init__(
        self, is_continuous: bool = False, bin_point_cloud_fields: Optional[Iterable[str]] = None
    ) -> None:
        self.is_continuous = is_continuous
        self.bin_point_cloud_fields = (
            list(bin_point_cloud_fields) if bin_point_cloud_fields else None
        )

    def __getitem__(self, key: str) -> Any:
        try:
            return getattr(self, key)
        except AttributeError as error:
            raise KeyError(key) from error

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a :class:`Notes` instance from the given contents.

        Arguments:
            contents: The given dict containing the dataset notes::

                    {
                        "isContinuous":            <boolean>
                        "binPointCloudFields": [   <array> or null
                                <field_name>,      <str>
                                ...
                        ]
                    }

        Returns:
            The loaded :class:`Notes` instance.

        """
        return common_loads(cls, contents)

    def keys(self) -> KeysView[str]:
        """Return the valid keys within the notes.

        Returns:
            The valid keys within the notes.

        """
        return KeysView(self._repr_attrs)  # type: ignore[arg-type]

    def dumps(self) -> Dict[str, Any]:
        """Dumps the notes into a dict.

        Returns:
            A dict containing all the information of the Notes::

                {
                    "isContinuous":           <boolean>
                    "binPointCloudFields": [  <array> or null
                        <field_name>,         <str>
                        ...
                    ]
                }

        """
        return self._dumps()


# When the NameMixin is before Sequence[_T], typing will raise AttributeError.
# related issue: python/typing#777
class DatasetBase(Sequence[_T], NameMixin):  # pylint: disable=too-many-ancestors
    """This class defines the concept of a basic dataset.

    DatasetBase represents a whole dataset contains several segments
    and is the base class of :class:`Dataset` and :class:`FusionDataset`.

    A dataset with labels should contain a :class:`~tensorbay.label.catalog.Catalog`
    indicating all the possible values of the labels.

    Arguments:
        name: The name of the dataset.
        gas: The :class:`~tensorbay.client.gas.GAS` client for getting a remote dataset.
        revision: The revision of the remote dataset.

    Attributes:
        catalog: The :class:`~tensorbay.label.catalog.Catalog` of the dataset.
        notes: The :class:`Notes` of the dataset.

    """

    _is_fusion: bool

    _repr_type = ReprType.SEQUENCE

    def __init__(
        self, name: str, gas: Optional["GAS"] = None, revision: Optional[str] = None
    ) -> None:
        super().__init__(name)

        if gas:
            self._client = gas.get_dataset(name, is_fusion=self._is_fusion)
            if revision:
                self._client.checkout(revision)
        else:
            self._segments: SortedNameList[_T] = SortedNameList()
            self._catalog = Catalog()
            self._notes = Notes()

    def __len__(self) -> int:
        return self._get_segments().__len__()

    @overload
    def __getitem__(self, index: Union[int, str]) -> _T:
        ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[_T]:
        ...

    def __getitem__(self, index: Union[int, str, slice]) -> Union[Sequence[_T], _T]:
        return self._get_segments().__getitem__(index)

    def __delitem__(self, index: Union[int, str, slice]) -> None:
        return self._get_segments().__delitem__(index)

    def __contains__(self, key: Any) -> bool:
        return self._get_segments().__contains__(key)

    @locked
    def _init_segments(self) -> None:
        self._segments = SortedNameList()

        for segment in self._client._list_segment_instances():  # pylint: disable=protected-access
            self._segments.add(segment)  # type: ignore[arg-type]

    def _get_segments(self) -> SortedNameList[_T]:
        if not hasattr(self, "_segments"):
            self._init_segments()

        return self._segments

    @property
    def catalog(self) -> Catalog:
        """Return the catalog of the dataset.

        Returns:
            The :class:`~tensorbay.label.catalog.Catalog` of the dataset.

        """
        if not hasattr(self, "_catalog"):
            self._catalog = self._client.get_catalog()

        return self._catalog

    @property
    def notes(self) -> Notes:
        """Return the notes of the dataset.

        Returns:
            The class:`Notes` of the dataset.

        """
        if not hasattr(self, "_notes"):
            self._notes = self._client.get_notes()

        return self._notes

    def keys(self) -> Tuple[str, ...]:
        """Get all segment names.

        Returns:
            A tuple containing all segment names.

        """
        return self._get_segments().keys()

    def load_catalog(self, filepath: str) -> None:
        """Load catalog from a json file.

        Arguments:
            filepath: The path of the json file which contains the catalog information.

        """
        with open(filepath, "r") as fp:
            contents = json.load(fp)
        self._catalog = Catalog.loads(contents)

    def add_segment(self, segment: _T) -> None:
        """Add a segment to the dataset.

        Arguments:
            segment: The segment to be added.

        """
        self._get_segments().add(segment)


class Dataset(DatasetBase[Segment]):
    """This class defines the concept of dataset.

    Dataset is made up of data collected from only one sensor or data without sensor information.
    It consists of a list of :class:`~tensorbay.dataset.segment.Segment`.

    """

    _is_fusion = False

    def create_segment(self, segment_name: str = "default") -> Segment:
        """Create a segment with the given name.

        Arguments:
            segment_name: The name of the segment to create, which default value is an empty string.

        Returns:
            The created :class:`~tensorbay.dataset.segment.Segment`.

        """
        segment = Segment(segment_name)
        self._get_segments().add(segment)
        return segment


class FusionDataset(DatasetBase[FusionSegment]):
    """This class defines the concept of fusion dataset.

    FusionDataset is made up of data collected from multiple sensors.
    It consists of a list of :class:`~tensorbay.dataset.segment.FusionSegment`.
    """

    _is_fusion = True

    def create_segment(self, segment_name: str = "default") -> FusionSegment:
        """Create a fusion segment with the given name.

        Arguments:
            segment_name: The name of the fusion segment to create,
                which default value is an empty string.

        Returns:
            The created :class:`~tensorbay.dataset.segment.FusionSegment`.

        """
        segment = FusionSegment(segment_name)
        self._get_segments().add(segment)
        return segment
