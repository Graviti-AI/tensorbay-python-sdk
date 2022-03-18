#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""The structure of the search result."""


from typing import Any, Dict, Generator, Optional, Tuple

from tensorbay.client.lazy import LazyPage, PagingList
from tensorbay.client.requests import Client
from tensorbay.client.statistics import Statistics
from tensorbay.dataset import Frame, RemoteData
from tensorbay.sensor.sensor import Sensors
from tensorbay.utility import URL, ReprMixin, config

_MASK_KEYS = ("semantic_mask", "instance_mask", "panoptic_mask")


class SearchResultBase(ReprMixin):
    """This class defines the structure of the search result.

    Arguments:
        job_id: The id of the search job.
        search_result_id: The id of the search result.
        client: The :class:`~tensorbay.client.requires.Client`.

    """

    _repr_attrs: Tuple[str, ...] = ("job_id", "search_result_id")

    def __init__(self, job_id: str, search_result_id: str, client: Client) -> None:
        self.job_id = job_id
        self.search_result_id = search_result_id
        self._client = client

    def _list_segments(self, offset: int = 0, limit: int = 128) -> Dict[str, Any]:
        params: Dict[str, Any] = {"draftNumber": 1, "offset": offset, "limit": limit}
        response = self._client.open_api_do("GET", "segments", self.search_result_id, params=params)
        return response.json()  # type: ignore[no-any-return]

    def _generate_segment_names(
        self, offset: int = 0, limit: int = 128
    ) -> Generator[Any, None, int]:
        response = self._list_segments(offset, limit)

        for item in response["segments"]:
            yield item["name"]

        return response["totalCount"]  # type: ignore[no-any-return]

    def _list_data_details(
        self, segment_name: str, offset: int = 0, limit: int = 128
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "segmentName": segment_name,
            "offset": offset,
            "limit": limit,
            "draftNumber": 1,
        }

        if config.is_internal:
            params["isInternal"] = True

        response = self._client.open_api_do(
            "GET", "data/details", self.search_result_id, params=params
        )
        return response.json()  # type: ignore[no-any-return]

    def _generate_urls(
        self, segment_name: str, offset: int = 0, limit: int = 128
    ) -> Generator[Dict[str, str], None, int]:
        response = self._list_data_details(segment_name, offset, limit)

        for item in response["dataDetails"]:
            yield item["url"]

        return response["totalCount"]  # type: ignore[no-any-return]

    def _generate_mask_urls(
        self, segment_name: str, mask_type: str, offset: int = 0, limit: int = 128
    ) -> Generator[Optional[str], None, int]:
        response = self._list_data_details(segment_name, offset, limit)

        for item in response["dataDetails"]:
            yield item["label"][mask_type] if item.get("label") and item.get("label").get(
                mask_type
            ) else None

        return response["totalCount"]  # type: ignore[no-any-return]

    def create_dataset(self, name: str, alias: str = "", is_public: bool = False) -> None:
        """Create a TensorBay dataset based on the search result.

        Arguments:
            name: Name of the dataset, unique for a user.
            alias: Alias of the dataset, default is "".
            is_public: Whether the dataset is a public dataset.

        """
        post_data = {
            "datasetName": name,
            "alias": alias,
            "isPublic": is_public,
        }

        self._client.open_api_do(
            "POST", f"searchResults/{self.search_result_id}/datasets", "", json=post_data
        )

    def get_label_statistics(self) -> Statistics:
        """Get label statistics of the search result.

        Returns:
            Required :class:`~tensorbay.client.dataset.Statistics`.

        """
        params: Dict[str, Any] = {"draftNumber": 1}
        return Statistics(
            self._client.open_api_do(
                "GET", "labels/statistics", self.search_result_id, params=params
            ).json()["labelStatistics"]
        )

    def list_segment_names(self) -> PagingList[str]:
        """List all segment names of the search result.

        Returns:
            The PagingList of segment names.

        """
        return PagingList(self._generate_segment_names, 128)


class SearchResult(SearchResultBase):
    """This class defines the structure of the search result from normal dataset."""

    def _generate_data(
        self, segment_name: str, offset: int = 0, limit: int = 128
    ) -> Generator[RemoteData, None, int]:
        response = self._list_data_details(segment_name, offset, limit)

        urls = LazyPage.from_items(
            offset,
            limit,
            lambda offset, limit: self._generate_urls(segment_name, offset, limit),
            (item["url"] for item in response["dataDetails"]),
        )

        mask_urls = {}
        for key in _MASK_KEYS:
            mask_urls[key] = LazyPage.from_items(
                offset,
                limit,
                lambda offset, limit, k=key.upper(): (  # type: ignore[misc]
                    self._generate_mask_urls(segment_name, k, offset, limit)
                ),
                (item["label"].get(key.upper(), {}).get("url") for item in response["dataDetails"]),
            )

        for i, item in enumerate(response["dataDetails"]):
            data = RemoteData.from_response_body(
                item,
                url=URL.from_getter(urls.items[i].get, urls.pull),
            )
            label = data.label
            for key in _MASK_KEYS:
                mask = getattr(label, key, None)
                if mask:
                    mask.url = URL.from_getter(mask_urls[key].items[i].get, mask_urls[key].pull)

            yield data

        return response["totalCount"]  # type: ignore[no-any-return]

    def list_data(self, segment_name: str) -> PagingList[RemoteData]:
        """List required data of the segment with given name.

        Arguments:
            segment_name: Name of the segment.

        Returns:
            The PagingList of :class:`~tensorbay.dataset.data.RemoteData`.

        """
        return PagingList(
            lambda offset, limit: self._generate_data(segment_name, offset, limit), 128
        )


class FusionSearchResult(SearchResultBase):
    """This class defines the structure of the search result from fusion dataset."""

    def _generate_frames(
        self, segment_name: str, offset: int = 0, limit: int = 128
    ) -> Generator[Frame, None, int]:
        response = self._list_data_details(segment_name, offset, limit)

        url_page = LazyPage.from_items(
            offset,
            limit,
            lambda offset, limit: self._generate_urls(segment_name, offset, limit),
            (
                {frame["sensorName"]: frame["url"] for frame in item["frame"]}
                for item in response["dataDetails"]
            ),
        )

        for index, item in enumerate(response["dataDetails"]):
            yield Frame.from_response_body(item, index, url_page)

        return response["totalCount"]  # type: ignore[no-any-return]

    def list_frames(self, segment_name: str) -> PagingList[Frame]:
        """List required frames of the segment with given name.

        Arguments:
            segment_name: Name of the segment.

        Returns:
            The PagingList of :class:`~tensorbay.dataset.frame.Frame`.

        """
        return PagingList(
            lambda offset, limit: self._generate_frames(segment_name, offset, limit), 128
        )

    def get_sensors(self, segment_name: str) -> Sensors:
        """Return the sensors of the segment with given name.

        Arguments:
            segment_name: Name of the segment.

        Returns:
            The :class:`sensors<~tensorbay.sensor.sensor.Sensors>` instance.

        """
        params: Dict[str, Any] = {"segmentName": segment_name, "draftNumber": 1}

        response = self._client.open_api_do(
            "GET", "sensors", self.search_result_id, params=params
        ).json()

        return Sensors.loads(response["sensors"])
