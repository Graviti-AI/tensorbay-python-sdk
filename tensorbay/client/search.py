#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""The structure of the search result."""

from typing import TYPE_CHECKING, Union

from tensorbay.client.lazy import PagingList
from tensorbay.client.requests import Client
from tensorbay.client.statistics import Statistics
from tensorbay.dataset import Frame, RemoteData
from tensorbay.sensor.sensor import Sensors
from tensorbay.utility import ReprMixin

if TYPE_CHECKING:
    from tensorbay.client.dataset import DatasetClient, FusionDatasetClient


class SearchResultBase(ReprMixin):
    """This class defines the structure of the search result.

    Arguments:
        job_id: The id of the search job.
        search_result_id: The id of the search result.
        client: The :class:`~tensorbay.client.requires.Client`.

    """

    def __init__(self, job_id: str, search_result_id: str, client: Client) -> None:
        pass

    def create_dataset(
        self, name: str, alias: str = "", is_public: bool = False
    ) -> Union["DatasetClient", "FusionDatasetClient"]:
        """Create a TensorBay dataset based on the search result.

        Arguments:
            name: Name of the dataset, unique for a user.
            alias: Alias of the dataset, default is "".
            is_public: Whether the dataset is a public dataset.

        Return:
            The created :class:`~tensorbay.client.dataset.DatasetClient` instance or
            :class:`~tensorbay.client.dataset.FusionDatasetClient` instance.

        """

    def get_label_statistics(self) -> Statistics:
        """Get label statistics of the search result.

        Return:
            Required :class:`~tensorbay.client.dataset.Statistics`.

        """

    def get_total_size(self) -> int:
        """Get total data size of the search result and the unit is byte.

        Return:
            The total data size of the search result.

        """

    def list_segment_names(self) -> PagingList[str]:
        """List all segment names of the search result.

        Return:
            The PagingList of segment names.

        """


class SearchResult(SearchResultBase):
    """This class defines the structure of the search result from normal dataset."""

    def list_data(self, segment_name: str) -> PagingList[RemoteData]:
        """List required data of the segment with given name.

        Arguments:
            segment_name: Name of the segment.

        Return:
            The PagingList of :class:`~tensorbay.dataset.data.RemoteData`.

        """


class FusionSearchResult(SearchResultBase):
    """This class defines the structure of the search result from fusion dataset."""

    def list_frames(self, segment_name: str) -> PagingList[Frame]:
        """List required frames of the segment with given name.

        Arguments:
            segment_name: Name of the segment.

        Return:
            The PagingList of :class:`~tensorbay.dataset.frame.Frame`.

        """

    def get_sensors(self, segment_name: str) -> Sensors:
        """Return the sensors of the segment with given name.

        Arguments:
            segment_name: Name of the segment.

        Return:
            The :class:`sensors<~tensorbay.sensor.sensor.Sensors>`instance.

        """
