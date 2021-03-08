#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Class DatasetClientBase, DatasetClient and FusionDatasetClient.

:class:`DatasetClient` is a remote concept. It contains the information
needed for determining a unique dataset on TensorBay, and provides a series of methods within
dataset scope, such as :meth:`DatasetClient.get_segment`, :meth:`DatasetClient.list_segment_names`,
:meth:`DatasetClient.commit <DatasetClientBase.commit>`, and so on.
In contrast to the :class:`DatasetClient`,
:class:`~tensorbay.dataset.dataset.Dataset` is a local concept. It represents a
dataset created locally. Please refer to
:class:`~tensorbay.dataset.dataset.Dataset` for more information.

Similar to the :class:`DatasetClient`, the
:class:`FusionDatasetClient` represents
the fusion dataset on TensorBay, and its local counterpart is
:class:`~tensorbay.dataset.dataset.FusionDataset`.
Please refer to :class:`~tensorbay.dataset.dataset.FusionDataset` for more information.

"""

import sys
from typing import Any, Dict, Iterable, Iterator, Optional, Tuple

from ..dataset import Data, Frame, FusionSegment, Segment
from ..label import Catalog
from .exceptions import GASSegmentError
from .requests import Client, multithread_upload, paging_range
from .segment import FusionSegmentClient, SegmentClient


class DatasetClientBase:
    """This class defines the basic concept of the dataset client.

    A :class:`DatasetClientBase` contains the information needed for
    determining a unique dataset on TensorBay, and provides a series of
    method within dataset scope, such as :meth:`DatasetClientBase.list_segment_names`
    and :meth:`DatasetClientBase.upload_catalog`.

    Arguments:
        name: Dataset name.
        dataset_id: Dataset ID.
        client: The client used for sending request to TensorBay.
        commit_id: The dataset commit ID.

    """

    def __init__(
        self, name: str, dataset_id: str, client: Client, commit_id: Optional[str] = None
    ) -> None:
        self._name = name
        self._dataset_id = dataset_id
        self._client = client
        self._commit_id = commit_id

    def _commit(self, message: str, tag: Optional[str] = None) -> str:
        post_data = {
            "message": message,
        }
        if tag:
            post_data["tag"] = tag

        response = self._client.open_api_do("POST", "", self.dataset_id, json=post_data)
        return response.json()["commitId"]  # type: ignore[no-any-return]

    def _create_segment(self, name: str) -> None:
        post_data = {"name": name}
        self._client.open_api_do("POST", "segments", self.dataset_id, json=post_data)

    def _list_segments(
        self, *, start: int = 0, stop: int = sys.maxsize, page_size: int = 128
    ) -> Iterator[Dict[str, str]]:
        params: Dict[str, Any] = {}
        if self._commit_id:
            params["commit"] = self._commit_id

        for params["offset"], params["limit"] in paging_range(start, stop, page_size):
            response = self._client.open_api_do(
                "GET", "segments", self.dataset_id, params=params
            ).json()
            yield from response["segments"]
            if response["recordSize"] + response["offset"] >= response["totalCount"]:
                break

    @property
    def commit_id(self) -> Optional[str]:
        """Return the commit ID.

        Returns:
            The commit ID.

        """
        return self._commit_id

    @property
    def dataset_id(self) -> str:
        """Return the TensorBay dataset ID.

        Returns:
            The TensorBay dataset ID.

        """
        return self._dataset_id

    def commit(self, message: str, tag: Optional[str] = None) -> None:
        """Commit the draft.

        Arguments:
            message: The commit message.
            tag: A tag for current commit.

        """
        commit_id = self._commit(message, tag)
        self._commit_id = commit_id

    def list_segment_names(self, *, start: int = 0, stop: int = sys.maxsize) -> Iterator[str]:
        """List all segment names in a certain commit.

        Arguments:
            start: The index to start.
            stop: The index to end.

        Yields:
            Required segment names.

        """
        yield from (segment["name"] for segment in self._list_segments(start=start, stop=stop))

    def get_catalog(self) -> Catalog:
        """Get the catalog of the certain commit.

        Returns:
            Required :class:`~tensorbay.label.catalog.Catalog`.

        """
        response = self._client.open_api_do("GET", "labels/catalogs", self.dataset_id).json()
        return Catalog.loads(response["catalog"])

    def upload_catalog(self, catalog: Catalog) -> None:
        """Upload a catalog to the draft.

        Arguments:
            catalog: :class:`~tensorbay.label.catalog.Catalog` to upload.

        Raises:
            TypeError: When the catalog is empty.

        """
        put_data = catalog.dumps()
        if not put_data:
            raise TypeError("Empty catalog")

        self._client.open_api_do("PUT", "labels/catalogs", self.dataset_id, json=put_data)

    def update_information(
        self, *, is_continuous: Optional[bool] = None, description: Optional[str] = None
    ) -> None:
        """Update information of draft with the given content.

        Arguments:
            is_continuous: Whether the TensorBay dataset is continuous.
            description: Description of the TensorBay dataset.

        """
        patch_data: Dict[str, Any] = {}
        if is_continuous is not None:
            patch_data["isContinuous"] = is_continuous
        if description is not None:
            patch_data["description"] = description

        self._client.open_api_do("PATCH", "", self.dataset_id, json=patch_data)

    def delete_segment(self, name: str) -> None:
        """Delete a segment of the draft.

        Arguments:
            name: Segment name.

        """
        delete_data = {"segmentName": name}

        self._client.open_api_do("DELETE", "segments", self.dataset_id, json=delete_data)


class DatasetClient(DatasetClientBase):
    """This class defines :class:`DatasetClient`.

    :class:`DatasetClient` inherits from :class:`DataClientBase` and
    provides more methods within a dataset scope, such as :meth:`DatasetClient.get_segment`,
    :meth:`DatasetClient.commit <DatasetClientBase.commit>` and
    :meth:`DatasetClient.upload_segment`.
    In contrast to :class:`FusionDatasetClient`, a
    :class:`DatasetClient` has only one sensor.

    """

    def get_or_create_segment(self, name: str = "") -> SegmentClient:
        """Create a segment with the given name to the draft.

        Arguments:
            name: Segment name, can not be "_default".

        Returns:
            Created :class:`~tensorbay.client.segment.SegmentClient` with given name.

        """
        if name not in self.list_segment_names():
            self._create_segment(name)
        return SegmentClient(name, self._dataset_id, self._name, self._client, self.commit_id)

    def get_segment(self, name: str = "") -> SegmentClient:
        """Get a segment in a certain commit according to given name.

        Arguments:
            name: The name of the required segment.

        Returns:
            The required class:`~tensorbay.client.segment.SegmentClient`.

        Raises:
            GASSegmentError: When the required segment does not exist.

        """
        if name not in self.list_segment_names():
            raise GASSegmentError(name)

        return SegmentClient(name, self._dataset_id, self._name, self._client, self.commit_id)

    def upload_segment(
        self,
        segment: Segment,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> SegmentClient:
        """Upload a :class:`~tensorbay.dataset.segment.Segment` to the dataset.

        This function will upload all info contains in
        the input :class:`~tensorbay.dataset.segment.Segment`,
        which includes:
        - Create a segment using the name of input Segment.
        - Upload all Data in the Segment to the dataset.

        Arguments:
            segment: The :class:`~tensorbay.dataset.segment.Segment`
                contains the information needs to be upload.
            jobs: The number of the max workers in multi-thread uploading method.
            skip_uploaded_files: True for skipping the uploaded files.

        Returns:
            The :class:`~tensorbay.client.segment.SegmentClient`
                used for uploading the data in the segment.

        """
        segment_client = self.get_or_create_segment(segment.name)
        local_data: Iterator[Data] = filter(
            lambda data: isinstance(data, Data), segment  # type: ignore[arg-type]
        )
        if skip_uploaded_files:
            done_set = set(segment_client.list_data_paths())
            segment_filter = filter(
                lambda data: data.target_remote_path not in done_set, local_data
            )
        else:
            segment_filter = local_data

        multithread_upload(segment_client.upload_data, segment_filter, jobs=jobs)
        return segment_client


class FusionDatasetClient(DatasetClientBase):
    """This class defines :class:`FusionDatasetClient`.

    :class:`FusionDatasetClient` inherits from :class:`DatasetClientBase` and
    provides more methods within a fusion dataset scope,
    such as :meth:`FusionDatasetClient.get_segment`,
    :meth:`FusionDatasetClient.commit <DatasetClientBase.commit>`
    and :meth:`FusionDatasetClient.upload_segment`.
    In contrast to :class:`DatasetClient`, a
    :class:`FusionDatasetClient` has multiple sensors.

    """

    def get_or_create_segment(self, name: str = "") -> FusionSegmentClient:
        """Create a fusion segment with the given name to the draft.

        Arguments:
            name: Segment name, can not be "_default".

        Returns:
            Created :class:`~tensorbay.client.segment.FusionSegmentClient` with given name.

        """
        if name not in self.list_segment_names():
            self._create_segment(name)
        return FusionSegmentClient(name, self._dataset_id, self._name, self._client, self.commit_id)

    def get_segment(self, name: str = "") -> FusionSegmentClient:
        """Get a fusion segment in a certain commit according to given name.

        Arguments:
            name: The name of the required fusion segment.

        Returns:
            The required class:`~tensorbay.client.segment.FusionSegmentClient`.

        Raises:
            GASSegmentError: When the required fusion segment does not exist.

        """
        if name not in self.list_segment_names():
            raise GASSegmentError(name)
        return FusionSegmentClient(name, self._dataset_id, self._name, self._client, self.commit_id)

    def upload_segment(
        self,
        segment: FusionSegment,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> FusionSegmentClient:
        """Upload a fusion segment object to the draft.

        This function will upload all info contains in the input
        :class:`~tensorbay.dataset.segment.FusionSegment`, which includes:

            - Create a segment using the name of input fusion segment object.
            - Upload all sensors in the segment to the dataset.
            - Upload all frames in the segment to the dataset.

        Arguments:
            segment: The :class:`~tensorbay.dataset.segment.FusionSegment`.
            jobs: The number of the max workers in multi-thread upload.
            skip_uploaded_files: Set it to True to skip the uploaded files.

        Returns:
            The :class:`~tensorbay.client.segment.FusionSegmentClient`
                used for uploading the data in the segment.

        """
        segment_client = self.get_or_create_segment(segment.name)
        for sensor in segment.sensors.values():
            segment_client.upload_sensor(sensor)

        segment_filter: Iterable[Tuple[int, Frame]]
        if skip_uploaded_files:
            # TODO: skip_uploaded_files
            segment_filter = enumerate(segment)
        else:
            segment_filter = enumerate(segment)

        multithread_upload(
            lambda args: segment_client.upload_frame(args[1], args[0]),
            segment_filter,
            jobs=jobs,
        )

        return segment_client
