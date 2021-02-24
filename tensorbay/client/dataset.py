#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Class DatasetClientBase, DatasetClient and FusionDatasetClient.

:class:`DatasetClient` is a remote concept. It contains the information
needed for determining a unique dataset on TensorBay, and provides a series of methods within
dataset scope, such as :meth:`DataClient.get_segment`,
:meth:`DataClient.list_segments`, :meth:`DataClient.commit`, and so on.
In contrast to the :class:`DatasetClient`, :class:`Dataset` is a local concept. It represents a
dataset created locally. Please refer to :class:`Dataset` for more information.

Similar to the :class:`DatasetClient`, the :class:`FusionDatasetClient` represents
the fusion dataset on TensorBay, and its local counterpart is :class:`FusionDataset`.
Please refer to :class:`FusionDataset` for more information.

Todo:
    Add `../dataset/dataset.py` link.
    Add `../label/catalog.py` link.
    Add `../dataset/segment.py`

"""

import sys
from typing import Any, Dict, Iterable, Iterator, Optional, Tuple

from ..dataset import Data, Frame, FusionSegment, Segment
from ..label import Catalog
from .exceptions import GASSegmentError
from .requests import Client, multithread_upload, paging_range
from .segment import FusionSegmentClient, SegmentClient


class DatasetClientBase:
    """This class defines the basic concept of :class:`DatasetClient`.

    A :class:`DatasetClientBase` contains the information needed for
    determining a unique dataset on TensorBay, and provides a series of
    method within dataset scope, such as :meth:`DatasetClient.list_segments`
    and :meth:`DatasetClient.upload_catalog`.

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

    @property
    def commit_id(self) -> Optional[str]:
        """Get the dataset commit ID.

        Returns:
            The dataset commit ID.

        """
        return self._commit_id

    @property
    def dataset_id(self) -> str:
        """Get the dataset ID.

        Returns:
            The dataset ID.

        """
        return self._dataset_id

    def _commit(self, message: str, tag: Optional[str] = None) -> str:
        post_data = {
            "message": message,
        }
        if tag:
            post_data["tag"] = tag

        response = self._client.open_api_do("POST", "", self.dataset_id, json=post_data)
        return response.json()["commitId"]  # type: ignore[no-any-return]

    def commit(self, message: str, tag: Optional[str] = None) -> None:
        """Commit the draft of dataset/fusion dataset.

        Arguments:
            message: The commit message of this commit.
            tag: A tag for current commit.

        """
        commit_id = self._commit(message, tag)
        self._commit_id = commit_id

    def _create_segment(self, name: str) -> None:
        post_data = {"name": name}
        self._client.open_api_do("POST", "segments", self.dataset_id, json=post_data)

    def _list_segments(
        self, *, start: int = 0, stop: int = sys.maxsize, page_size: int = 128
    ) -> Iterator[str]:
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

    def list_segments(self, *, start: int = 0, stop: int = sys.maxsize) -> Iterator[str]:
        """List all segment names in a dataset.

        Arguments:
            start: The segment index to start.
            stop: The segment index to end.

        Returns:
            Required segment names.

        """
        return self._list_segments(start=start, stop=stop)

    def get_catalog(self) -> Catalog:
        """Get the catalog of the Tensorbay dataset.

        Returns:
            Required :class:`Catalog`.

        """
        response = self._client.open_api_do("GET", "labels/catalogs", self.dataset_id).json()
        return Catalog.loads(response["catalog"])

    def upload_catalog(self, catalog: Catalog) -> None:
        """Upload a :class:`Catalog` to the dataset.

        Arguments:
            catalog: :class:`Catalog` to upload.

        Raises:
            TypeError: If the catalog is empty.

        """
        put_data = catalog.dumps()
        if not put_data:
            raise TypeError("Empty catalog")

        self._client.open_api_do("PUT", "labels/catalogs", self.dataset_id, json=put_data)

    def update_information(
        self, *, is_continuous: Optional[bool] = None, description: Optional[str] = None
    ) -> None:
        """Update information in draft of TensorBay dataset with the given content.

        Arguments:
            is_continuous: Whether the dataset is continuous.
            description: Description of the dataset.

        """
        patch_data: Dict[str, Any] = {}
        if is_continuous is not None:
            patch_data["isContinuous"] = is_continuous
        if description is not None:
            patch_data["description"] = description

        self._client.open_api_do("PATCH", "", self.dataset_id, json=patch_data)

    def delete_segment(self, name: str) -> None:
        """Delete a segment in Tensorbay dataset.

        Arguments:
            name: Segment name.

        """
        delete_data = {"segmentName": name}

        self._client.open_api_do("DELETE", "segments", self.dataset_id, json=delete_data)


class DatasetClient(DatasetClientBase):
    """This class defines :class:`DatasetClient`.

    :class:`DatasetClient` inherits from :class:`DataClientBase` and
    provides more methods within a dataset scope, such as :meth:`DatasetClient.get_segment`,
    :meth:`DatasetClient.commit` and :meth:`DatasetClient.upload_segment_object`.
    In contrast to :class:`FusionDatasetClient`, a :class:`DatasetClient` has only one sensor.

    """

    def get_or_create_segment(self, name: str = "") -> SegmentClient:
        """Create a segment set according to given name.

        Arguments:
            name: Segment name, can not be "_default".

        Returns:
            Created segment with given name, or created default segment.

        """
        if name not in self._list_segments():
            self._create_segment(name)
        return SegmentClient(name, self._dataset_id, self._name, self._client, self.commit_id)

    def get_segment(self, name: str = "") -> SegmentClient:
        """Get a segment according to given name.

        Arguments:
            name: The name of the required segment.

        Returns:
            The required segment.

        Raises:
            GASSegmentError: If the required segment does not exist.

        """
        if name not in self._list_segments():
            raise GASSegmentError(name)

        return SegmentClient(name, self._dataset_id, self._name, self._client, self.commit_id)

    def get_segment_object(self, name: str = "") -> Segment:
        """Get a :class:`Segment` according to given name.

        Arguments:
            name: The name of the required :class:`Segment`.

        Returns:
            The required :class:`Segment`.

        """
        segment_client = self.get_segment(name)
        segment = Segment(name)
        for data in segment_client.list_data_objects():
            segment.append(data)

        return segment

    def upload_segment_object(
        self,
        segment: Segment,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> SegmentClient:
        """Upload a :class:`Segment` to the dataset.

        This function will upload all info contains in the input :class:`Segment`,
        which includes:
            - Create a segment using the name of input :class:`Segment`.
            - Upload all Data in the :class:`Segment` to the dataset.

        Arguments:
            segment: The :class:`Segment` contains the information needs to be upload.
            jobs: The number of the max workers in multi-thread uploading method.
            skip_uploaded_files: True for skipping the uploaded files.

        Returns:
            The client used for uploading the data in the Segment.

        """
        segment_client = self.get_or_create_segment(segment.name)
        segment_filter: Iterable[Data]
        if skip_uploaded_files:
            done_set = set(segment_client.list_data())
            segment_filter = filter(lambda data: data.remote_path not in done_set, segment)
        else:
            segment_filter = segment

        multithread_upload(segment_client.upload_data_object, segment_filter, jobs=jobs)
        return segment_client


class FusionDatasetClient(DatasetClientBase):
    """This class defines :class:`FusionDatasetClient`.

    :class:`FusionDatasetClient` inherits from :class:`DataClientBase` and
    provides more methods within a fusion dataset scope,
    such as :meth:`FusionDataset.get_segment`, :meth:`FusionDataset.commit`
    and :meth:`FusionDataset.upload_segment_object`.
    In contrast to :class:`DatasetClient`, a :class:`FusionDatasetClient` has multiple sensors.

    """

    def get_or_create_segment(self, name: str = "") -> FusionSegmentClient:
        """Create a fusion segment set according to the given name.

        Arguments:
            name: Segment name, can not be "_default".

        Returns:
            Created fusion segment with given name, or created default segment.

        """
        if name not in self._list_segments():
            self._create_segment(name)
        return FusionSegmentClient(name, self._dataset_id, self._name, self._client, self.commit_id)

    def get_segment(self, name: str = "") -> FusionSegmentClient:
        """Get a fusion segment according to given name.

        Arguments:
            name: The name of the required fusion segment.

        Returns:
            The required fusion segment.

        Raises:
            GASSegmentError: If the required fusion segment does not exist.

        """
        if name not in self._list_segments():
            raise GASSegmentError(name)
        return FusionSegmentClient(name, self._dataset_id, self._name, self._client, self.commit_id)

    def get_segment_object(self, name: str = "") -> FusionSegment:
        """Get a :class:`Segment` according to given name.

        Arguments:
            name: The name of the required :class:`Segment`.

        Returns:
            The required :class:`Segment`.

        """
        segment_client = self.get_segment(name)
        segment = FusionSegment(name)
        for sensor in segment_client.list_sensor_objects():
            segment.sensors.add(sensor)
        for frame in segment_client.list_frame_objects():
            segment.append(frame)
        return segment

    def upload_segment_object(
        self,
        segment: FusionSegment,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> FusionSegmentClient:
        """Upload a :class:`FusionSegment` to the dataset.

        This function will upload all info contains in the input :class:`FusionSegment`,
        which includes:
            - Create a segment using the name of input :class:`FusionSegment`.
            - Upload all Sensor in the segment to the dataset.
            - Upload all Frame in the segment to the dataset.

        Arguments:
            segment: The :class:`FusionSegment` needs to be uploaded.
            jobs: The number of the max workers in multi-thread upload.
            skip_uploaded_files: Set it to True to skip the uploaded files.

        Returns:
            The client used for uploading the data in the :class:`FusionSegment`.

        """
        segment_client = self.get_or_create_segment(segment.name)
        for sensor in segment.sensors.values():
            segment_client.upload_sensor_object(sensor)

        segment_filter: Iterable[Tuple[int, Frame]]
        if skip_uploaded_files:
            # TODO: skip_uploaded_files
            segment_filter = enumerate(segment)
        else:
            segment_filter = enumerate(segment)

        multithread_upload(
            lambda args: segment_client.upload_frame_object(args[1], args[0]),
            segment_filter,
            jobs=jobs,
        )

        return segment_client
