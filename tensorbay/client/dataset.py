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
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional, Tuple

from ..dataset import Data, Frame, FusionSegment, Segment
from ..label import Catalog
from .commit_status import CommitStatus
from .exceptions import GASSegmentError
from .requests import Client, multithread_upload, paging_range
from .segment import FusionSegmentClient, SegmentClient

if TYPE_CHECKING:
    from .gas import GAS


class DatasetClientBase:
    """This class defines the basic concept of the dataset client.

    A :class:`DatasetClientBase` contains the information needed for
    determining a unique dataset on TensorBay, and provides a series of
    method within dataset scope, such as :meth:`DatasetClientBase.list_segment_names`
    and :meth:`DatasetClientBase.upload_catalog`.

    Arguments:
        name: Dataset name.
        dataset_id: Dataset ID.
        gas_client: The initial client to interact between local and TensorBay.

    """

    _client: Client

    def __init__(
        self, name: str, dataset_id: str, gas_client: "GAS", *, commit_id: Optional[str] = None
    ) -> None:
        self._name = name
        self._dataset_id = dataset_id
        self._gas_client = gas_client
        self._client = gas_client._client  # pylint: disable=protected-access

        self._status = CommitStatus()
        if commit_id:
            self.checkout(commit=commit_id)

    def _commit(self, message: str, tag: Optional[str] = None) -> str:
        post_data: Dict[str, Any] = {
            "message": message,
        }
        post_data.update(self._status.get_status_info())

        if tag:
            post_data["tag"] = tag

        response = self._client.open_api_do("POST", "", self.dataset_id, json=post_data)
        return response.json()["commitId"]  # type: ignore[no-any-return]

    def _create_draft(self, title: Optional[str] = None) -> int:
        post_data: Dict[str, Any] = {}

        if title:
            post_data["title"] = title

        response = self._client.open_api_do("POST", "drafts", self.dataset_id, json=post_data)
        return response.json()["draftNumber"]  # type: ignore[no-any-return]

    def _list_drafts(
        self, *, start: int = 0, stop: int = sys.maxsize, page_size: int = 128
    ) -> Iterator[Dict[str, str]]:
        params: Dict[str, Any] = {}

        for params["offset"], params["limit"] in paging_range(start, stop, page_size):
            response = self._client.open_api_do(
                "GET", "drafts", self.dataset_id, params=params
            ).json()
            yield from response["drafts"]
            if response["recordSize"] + response["offset"] >= response["totalCount"]:
                break

    def _create_segment(self, name: str) -> None:
        post_data: Dict[str, Any] = {"name": name}
        post_data.update(self._status.get_status_info())

        self._client.open_api_do("POST", "segments", self.dataset_id, json=post_data)

    def _list_segments(
        self, *, start: int = 0, stop: int = sys.maxsize, page_size: int = 128
    ) -> Iterator[Dict[str, str]]:
        params: Dict[str, Any] = self._status.get_status_info()

        for params["offset"], params["limit"] in paging_range(start, stop, page_size):
            response = self._client.open_api_do(
                "GET", "segments", self.dataset_id, params=params
            ).json()
            yield from response["segments"]
            if response["recordSize"] + response["offset"] >= response["totalCount"]:
                break

    @property
    def name(self) -> str:
        """Return the TensorBay dataset name.

        Returns:
            The TensorBay dataset name.

        """
        return self._name

    @property
    def dataset_id(self) -> str:
        """Return the TensorBay dataset ID.

        Returns:
            The TensorBay dataset ID.

        """
        return self._dataset_id

    @property
    def status(self) -> CommitStatus:
        """Return the status of the dataset client.

        Returns:
            The status of the dataset client.

        """
        return self._status

    def create_draft(self, title: Optional[str] = None) -> int:
        """Create the draft.

        Arguments:
            title: The draft title.

        Returns:
            The draft number of the created draft

        """
        self._status.check_authority_for_commit()
        draft_number = self._create_draft(title)
        self._status.checkout(draft_number=draft_number)
        return draft_number

    def list_draft_titles_and_numbers(
        self, *, start: int = 0, stop: int = sys.maxsize
    ) -> Iterator[Dict[str, str]]:
        """List the dict containing title and number of drafts.

        Arguments:
            start: The index to start.
            stop: The index to end.

        Yields:
            The dict containing title and number of drafts.

        """
        yield from self._list_drafts(start=start, stop=stop)

    def checkout(self, commit: Optional[str] = None, draft_number: Optional[int] = None) -> None:
        """Checkout to commit or draft.

        Arguments:
            commit: The commit ID.
            draft_number: The draft number.

        Raises:
            TypeError: When both commit ID and draft number are provided or neither.

        """
        if commit is None and draft_number is None:
            raise TypeError("Neither commit ID nor draft number is given, please give one ID")
        if commit is not None and draft_number is not None:
            raise TypeError("Both commit ID and draft number are given, please only give one ID")

        self._status.checkout(commit=commit, draft_number=draft_number)

    def commit(self, message: str, *, tag: Optional[str] = None) -> None:
        """Commit the draft.

        Arguments:
            message: The commit message.
            tag: A tag for current commit.

        """
        self._status.check_authority_for_draft()
        self._status.checkout(commit=self._commit(message, tag))

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
        params: Dict[str, Any] = self._status.get_status_info()

        response = self._client.open_api_do(
            "GET", "labels/catalogs", self.dataset_id, params=params
        ).json()
        return Catalog.loads(response["catalog"])

    def upload_catalog(self, catalog: Catalog) -> None:
        """Upload a catalog to the draft.

        Arguments:
            catalog: :class:`~tensorbay.label.catalog.Catalog` to upload.

        Raises:
            TypeError: When the catalog is empty.

        """
        self._status.check_authority_for_draft()

        put_data: Dict[str, Any] = {"catalog": catalog.dumps()}
        if not put_data:
            raise TypeError("Empty catalog")
        put_data.update(self._status.get_status_info())

        self._client.open_api_do("PUT", "labels/catalogs", self.dataset_id, json=put_data)

    def delete_segment(self, name: str) -> None:
        """Delete a segment of the draft.

        Arguments:
            name: Segment name.

        """
        self._status.check_authority_for_draft()

        delete_data: Dict[str, Any] = {"segmentName": name}
        delete_data.update(self._status.get_status_info())

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
        self._status.check_authority_for_draft()
        if name not in self.list_segment_names():
            self._create_segment(name)
        return SegmentClient(name, self)

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

        return SegmentClient(name, self)

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
        self._status.check_authority_for_draft()

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
        self._status.check_authority_for_draft()

        if name not in self.list_segment_names():
            self._create_segment(name)
        return FusionSegmentClient(name, self)

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
        return FusionSegmentClient(name, self)

    def upload_segment(
        self,
        segment: FusionSegment,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,  # pylint: disable=unused-argument
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

        Raises:
            TypeError: When all the frames have the same patterns(both have frame id or not).

        Returns:
            The :class:`~tensorbay.client.segment.FusionSegmentClient`
                used for uploading the data in the segment.

        """
        self._status.check_authority_for_draft()

        segment_client = self.get_or_create_segment(segment.name)
        for sensor in segment.sensors.values():
            segment_client.upload_sensor(sensor)

        segment_filter: Iterator[Tuple[Frame, Optional[int]]]

        if not segment:
            return segment_client

        have_frame_id = hasattr(segment[0], "frame_id")

        for frame in segment:
            if not hasattr(frame, "frame_id") == have_frame_id:
                raise TypeError(
                    "All the frames should have the same patterns(both have frame id or not)."
                )

        if have_frame_id:
            segment_filter = ((frame, None) for frame in segment)
        else:
            segment_filter = ((frame, 10 * index + 10) for index, frame in enumerate(segment))

        multithread_upload(
            lambda args: segment_client.upload_frame(*args),
            segment_filter,
            jobs=jobs,
        )

        return segment_client
