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

import logging
from typing import TYPE_CHECKING, Any, Dict, Generator, Iterable, Iterator, Optional, Tuple, Union

from ulid import ULID, from_timestamp

from ..dataset import AuthData, Data, Frame, FusionSegment, Notes, RemoteData, Segment
from ..exception import (
    FrameError,
    InvalidParamsError,
    NameConflictError,
    OperationError,
    ResourceNotExistError,
)
from ..label import Catalog
from .lazy import PagingList
from .log import UPLOAD_SEGMENT_RESUME_TEMPLATE
from .requests import Tqdm, multithread_upload
from .segment import _STRATEGIES, FusionSegmentClient, SegmentClient
from .status import Status
from .version import VersionControlClient

if TYPE_CHECKING:
    from .gas import GAS

logger = logging.getLogger(__name__)


class DatasetClientBase(VersionControlClient):
    """This class defines the basic concept of the dataset client.

    A :class:`DatasetClientBase` contains the information needed for
    determining a unique dataset on TensorBay, and provides a series of
    method within dataset scope, such as :meth:`DatasetClientBase.list_segment_names`
    and :meth:`DatasetClientBase.upload_catalog`.

    Arguments:
        name: Dataset name.
        dataset_id: Dataset ID.
        gas: The initial client to interact between local and TensorBay.
        status: The version control status of the dataset.
        alias: Dataset alias.

    Attributes:
        name: Dataset name.
        dataset_id: Dataset ID.
        status: The version control status of the dataset.
        alias: Dataset alias.

    """

    def __init__(
        self, name: str, dataset_id: str, gas: "GAS", *, status: Status, alias: str = ""
    ) -> None:
        super().__init__(dataset_id, gas, status=status)
        self._name = name
        self._alias = alias

    def _create_segment(self, name: str) -> None:
        post_data: Dict[str, Any] = {"name": name}
        post_data.update(self._status.get_status_info())

        self._client.open_api_do("POST", "segments", self._dataset_id, json=post_data)

    def _list_segments(self, offset: int = 0, limit: int = 128) -> Dict[str, Any]:
        params: Dict[str, Any] = self._status.get_status_info()
        params["offset"] = offset
        params["limit"] = limit

        response = self._client.open_api_do("GET", "segments", self._dataset_id, params=params)
        return response.json()  # type: ignore[no-any-return]

    def _generate_segment_names(
        self, offset: int = 0, limit: int = 128
    ) -> Generator[str, None, int]:
        response = self._list_segments(offset, limit)

        for item in response["segments"]:
            yield item["name"]

        return response["totalCount"]  # type: ignore[no-any-return]

    def _copy_segment(
        self,
        source_name: str,
        target_name: str,
        *,
        source_client: Union[None, "DatasetClient", "FusionDatasetClient"],
        strategy: str = "abort",
    ) -> None:
        if strategy not in _STRATEGIES:
            raise InvalidParamsError(param_name="strategy", param_value=strategy)

        source = {"segmentName": source_name}

        if not source_client:
            if source_name == target_name:
                raise OperationError("Copying the segment to the same location is not allowed")
        else:
            source["id"] = source_client.dataset_id
            source.update(source_client.status.get_status_info())

        self._status.check_authority_for_draft()

        post_data: Dict[str, Any] = {
            "strategy": strategy,
            "source": source,
            "segmentName": target_name,
        }
        post_data.update(self._status.get_status_info())

        self._client.open_api_do("POST", "segments?copy", self._dataset_id, json=post_data)

    def _move_segment(
        self,
        source_name: str,
        target_name: str,
        *,
        strategy: str = "abort",
    ) -> None:
        self._status.check_authority_for_draft()
        if strategy not in _STRATEGIES:
            raise InvalidParamsError(param_name="strategy", param_value=strategy)
        post_data: Dict[str, Any] = {
            "strategy": strategy,
            "source": {"segmentName": source_name},
            "segmentName": target_name,
        }
        post_data.update(self._status.get_status_info())

        self._client.open_api_do("POST", "segments?move", self._dataset_id, json=post_data)

    @property
    def name(self) -> str:
        """Return the TensorBay dataset name.

        Returns:
            The TensorBay dataset name.

        """
        return self._name

    @property
    def alias(self) -> str:
        """Return the TensorBay dataset alias.

        Returns:
            The TensorBay dataset alias.

        """
        return self._alias

    def update_notes(
        self,
        *,
        is_continuous: Optional[bool] = None,
        bin_point_cloud_fields: Union[Iterable[str], None] = ...,  # type: ignore[assignment]
    ) -> None:
        """Update the notes.

        Arguments:
            is_continuous: Whether the data is continuous.
            bin_point_cloud_fields: The field names of the bin point cloud files in the dataset.

        """
        self._status.check_authority_for_draft()

        patch_data: Dict[str, Any] = {}
        if is_continuous is not None:
            patch_data["isContinuous"] = is_continuous

        if bin_point_cloud_fields is None:
            patch_data["binPointCloudFields"] = bin_point_cloud_fields
        elif bin_point_cloud_fields is not ...:  # type: ignore[comparison-overlap]
            patch_data["binPointCloudFields"] = list(bin_point_cloud_fields)

        patch_data.update(self._status.get_status_info())

        self._client.open_api_do("PATCH", "notes", self._dataset_id, json=patch_data)

    def get_notes(self) -> Notes:
        """Get the notes.

        Returns:
            The :class:`~tensorbay.dataset.dataset.Notes`.

        """
        params: Dict[str, Any] = self._status.get_status_info()

        return Notes.loads(
            self._client.open_api_do("GET", "notes", self._dataset_id, params=params).json()
        )

    def list_segment_names(self) -> PagingList[str]:
        """List all segment names in a certain commit.

        Returns:
            The PagingList of segment names.

        """
        return PagingList(self._generate_segment_names, 128)

    def get_catalog(self) -> Catalog:
        """Get the catalog of the certain commit.

        Returns:
            Required :class:`~tensorbay.label.catalog.Catalog`.

        """
        params: Dict[str, Any] = self._status.get_status_info()

        response = self._client.open_api_do(
            "GET", "labels/catalogs", self._dataset_id, params=params
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

        self._client.open_api_do("PUT", "labels/catalogs", self._dataset_id, json=put_data)

    def delete_segment(self, name: str) -> None:
        """Delete a segment of the draft.

        Arguments:
            name: Segment name.

        """
        self._status.check_authority_for_draft()

        delete_data: Dict[str, Any] = {"segmentName": name}
        delete_data.update(self._status.get_status_info())

        self._client.open_api_do("DELETE", "segments", self._dataset_id, json=delete_data)


class DatasetClient(DatasetClientBase):
    """This class defines :class:`DatasetClient`.

    :class:`DatasetClient` inherits from :class:`DataClientBase` and
    provides more methods within a dataset scope, such as :meth:`DatasetClient.get_segment`,
    :meth:`DatasetClient.commit <DatasetClientBase.commit>` and
    :meth:`DatasetClient.upload_segment`.
    In contrast to :class:`FusionDatasetClient`, a
    :class:`DatasetClient` has only one sensor.

    """

    def _generate_segments(
        self, offset: int = 0, limit: int = 128
    ) -> Generator[Segment, None, int]:
        response = self._list_segments(offset, limit)

        for item in response["segments"]:
            segment = Segment._from_client(  # pylint: disable=protected-access
                SegmentClient(item["name"], self)
            )
            segment.description = item["description"]
            yield segment

        return response["totalCount"]  # type: ignore[no-any-return]

    def _generate_diff_segments(
        self, basehead: str, offset: int = 0, limit: int = 128
    ) -> Generator[Dict[str, Any], None, int]:
        params: Dict[str, Any] = {"offset": offset, "limit": limit}

        response = self._client.open_api_do(
            "GET", f"diffs/{basehead}/segments", self._dataset_id, param=params
        ).json()

        yield from response["segments"]
        return response["totalCount"]  # type: ignore[no-any-return]

    def _list_segment_instances(self) -> PagingList[Segment]:
        return PagingList(self._generate_segments, 128)

    def _upload_segment(
        self,
        segment: Segment,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
        pbar: Tqdm,
    ) -> SegmentClient:
        segment_client = self.get_or_create_segment(segment.name)
        all_data: Iterator[Union[AuthData, Data]] = filter(
            lambda data: pbar.update_for_skip(not isinstance(data, RemoteData)),
            segment,  # type: ignore[arg-type]
        )
        if skip_uploaded_files:
            done_set = set(segment_client.list_data_paths())
            segment_filter = filter(
                lambda data: pbar.update_for_skip(data.target_remote_path not in done_set),
                all_data,
            )
        else:
            segment_filter = all_data

        multithread_upload(
            # pylint: disable=protected-access
            segment_client._upload_or_import_data,
            segment_filter,
            callback=segment_client._synchronize_upload_info,
            jobs=jobs,
            pbar=pbar,
        )
        return segment_client

    def get_or_create_segment(self, name: str = "default") -> SegmentClient:
        """Get or create a segment with the given name.

        Arguments:
            name: The name of the fusion segment.

        Returns:
            The created :class:`~tensorbay.client.segment.SegmentClient` with given name.

        """
        self._status.check_authority_for_draft()
        if name not in self.list_segment_names():
            self._create_segment(name)
        return SegmentClient(name, self)

    def create_segment(self, name: str = "default") -> SegmentClient:
        """Create a segment with the given name.

        Arguments:
            name: The name of the fusion segment.

        Returns:
            The created :class:`~tensorbay.client.segment.SegmentClient` with given name.

        Raises:
            NameConflictError: When the segment exists.

        """
        self._status.check_authority_for_draft()
        if name not in self.list_segment_names():
            self._create_segment(name)
        else:
            raise NameConflictError(resource="segment", identification=name)
        return SegmentClient(name, self)

    def copy_segment(
        self,
        source_name: str,
        target_name: Optional[str] = None,
        *,
        source_client: Optional["DatasetClient"] = None,
        strategy: str = "abort",
    ) -> SegmentClient:
        """Copy segment to this dataset.

        Arguments:
            source_name: The source name of the copied segment.
            target_name: The target name of the copied segment.
                This argument is used to specify a new name of the copied segment.
                If None, the name of the copied segment will not be changed after copy.
            source_client: The source dataset client of the copied segment.
                This argument is used to specify where the copied segment comes from when the
                copied segment is from another commit, draft or even another dataset.
                If None, the copied segment comes from this dataset.
            strategy: The strategy of handling the name conflict. There are three options:

                1. "abort": stop copying and raise exception;
                2. "override": the source segment will override the origin segment;
                3. "skip": keep the origin segment.

        Returns:
            The client of the copied target segment.

        """
        if not target_name:
            target_name = source_name
        self._copy_segment(source_name, target_name, source_client=source_client, strategy=strategy)

        return SegmentClient(target_name, self)

    def move_segment(
        self,
        source_name: str,
        target_name: str,
        *,
        strategy: str = "abort",
    ) -> SegmentClient:
        """Move/Rename segment in this dataset.

        Arguments:
            source_name: The source name of the moved segment.
            target_name: The target name of the moved segment.
            strategy: The strategy of handling the name conflict. There are three options:

                1. "abort": stop moving and raise exception;
                2. "override": the source segment will override the origin segment;
                3. "skip": keep the origin segment.

        Returns:
            The client of the moved target segment.

        """
        self._move_segment(source_name, target_name, strategy=strategy)
        return SegmentClient(target_name, self)

    def get_segment(self, name: str = "default") -> SegmentClient:
        """Get a segment in a certain commit according to given name.

        Arguments:
            name: The name of the required segment.

        Returns:
            The required :class:`~tensorbay.client.segment.SegmentClient`.

        Raises:
            ResourceNotExistError: When the required segment does not exist.

        """
        if name not in self.list_segment_names():
            raise ResourceNotExistError(resource="segment", identification=name)

        return SegmentClient(name, self)

    def upload_segment(
        self,
        segment: Segment,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
        quiet: bool = False,
    ) -> SegmentClient:
        """Upload a :class:`~tensorbay.dataset.segment.Segment` to the dataset.

        This function will upload all info contains in
        the input :class:`~tensorbay.dataset.segment.Segment`, which includes:

            - Create a segment using the name of input Segment.
            - Upload all Data in the Segment to the dataset.

        Arguments:
            segment: The :class:`~tensorbay.dataset.segment.Segment`
                contains the information needs to be upload.
            jobs: The number of the max workers in multi-thread uploading method.
            skip_uploaded_files: True for skipping the uploaded files.
            quiet: Set to True to stop showing the upload process bar.

        Raises:
            Exception: When the upload got interrupted by Exception.

        Returns:
            The :class:`~tensorbay.client.segment.SegmentClient`
            used for uploading the data in the segment.

        """
        self._status.check_authority_for_draft()
        try:
            with Tqdm(len(segment), disable=quiet) as pbar:
                return self._upload_segment(
                    segment,
                    jobs=jobs,
                    skip_uploaded_files=skip_uploaded_files,
                    pbar=pbar,
                )
        except Exception:
            logger.error(
                UPLOAD_SEGMENT_RESUME_TEMPLATE,
                self._status.draft_number,
                self._status.draft_number,
            )
            raise

    def _list_diff_segments(
        self, *, source: Optional[Union[str, int]] = None, target: Optional[Union[str, int]] = None
    ) -> PagingList[Dict[str, Any]]:
        """List diffs of each segment between two versions.

        Arguments:
            source: Source version identification. Type int for draft number, type str for revision.
                If is not given, use the current version.
            target: Target version identification. Type int for draft number, type str for revision.
                If is not given, use the parent commit id.

        Examples:
            >>> self._list_diff_segments(source="b382450220a64ca9b514dcef27c82d9a", target=1)
            {
                "segments": [
                    {
                        "name": "Segment1",
                        "action": "add",
                        "data": {
                            "stats": {
                                "total": 3,
                                "additions": 3,
                                "deletions": 0,
                                "modifications": 0
                            },
                        },
                        "sensors": {
                            "action": "modify"
                        }
                    },
                    {
                        "name": "Segment2",
                        "action": "add",
                        "data": {
                            "stats": {
                                "total": 3,
                                "additions": 3,
                                "deletions": 0,
                               "modifications": 0
                            },
                        },
                        "sensors": {
                            "action": "modify"
                        }
                    },
                ]
                ...
                "offset": 0,
                "recordSize": 2,
                "totalCount": 2
            }

        Returns:
            The PagingList of diffs of each segment.

        """
        basehead = self._get_basehead(source, target)

        return PagingList(
            lambda offset, limit: self._generate_diff_segments(basehead, offset, limit), 128
        )


FrameDataGenerator = Iterator[Tuple[Union[Data, AuthData], str, str]]


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

    @staticmethod
    def _extract_all_data(
        source_frames: Iterator[Tuple[Frame, ULID]],
        pbar: Tqdm,
    ) -> FrameDataGenerator:
        for frame, frame_id in source_frames:
            for sensor_name, data in frame.items():
                if isinstance(data, RemoteData):
                    pbar.update()
                    continue

                yield data, sensor_name, frame_id.str

    @staticmethod
    def _extract_unuploaded_data(
        source_frames: Iterator[Tuple[Frame, ULID]], pbar: Tqdm, *, done_frames: Dict[float, Frame]
    ) -> FrameDataGenerator:
        for frame, frame_id in source_frames:
            done_frame = done_frames.get(frame_id.timestamp().timestamp)
            if done_frame:
                frame_id = done_frame.frame_id
            for sensor_name, data in frame.items():
                if isinstance(data, RemoteData):
                    pbar.update()
                    continue

                if (
                    done_frame
                    and sensor_name in done_frame
                    and done_frame[sensor_name].path == data.target_remote_path
                ):
                    pbar.update()
                    continue

                yield data, sensor_name, frame_id.str

    def _generate_segments(
        self, offset: int = 0, limit: int = 128
    ) -> Generator[FusionSegment, None, int]:
        response = self._list_segments(offset, limit)

        for item in response["segments"]:
            segment = FusionSegment._from_client(  # pylint: disable=protected-access
                FusionSegmentClient(item["name"], self)
            )
            segment.description = item["description"]
            yield segment

        return response["totalCount"]  # type: ignore[no-any-return]

    def _list_segment_instances(self) -> PagingList[FusionSegment]:
        return PagingList(self._generate_segments, 128)

    def _upload_segment(
        self,
        segment: FusionSegment,
        *,
        jobs: int,
        skip_uploaded_files: bool,
        pbar: Tqdm,
    ) -> FusionSegmentClient:
        segment_client = self.get_or_create_segment(segment.name)
        for sensor in segment.sensors:
            segment_client.upload_sensor(sensor)

        if not segment:
            return segment_client

        have_frame_id = hasattr(segment[0], "frame_id")

        for frame in segment:
            if hasattr(frame, "frame_id") != have_frame_id:
                raise FrameError(
                    "All the frames should have the same patterns(all have frame id or not)."
                )

        if have_frame_id:
            source_frames = ((frame, frame.frame_id) for frame in segment)
        else:
            source_frames = (
                (frame, from_timestamp(10 * index + 10)) for index, frame in enumerate(segment)
            )

        done_frames: Dict[float, Frame] = {
            frame.frame_id.timestamp().timestamp: frame for frame in segment_client.list_frames()
        }

        if not skip_uploaded_files:
            data_to_upload = FusionDatasetClient._extract_all_data(source_frames, pbar)
        else:
            data_to_upload = FusionDatasetClient._extract_unuploaded_data(
                source_frames, pbar, done_frames=done_frames
            )

        multithread_upload(
            # pylint: disable=protected-access
            lambda args: segment_client._upload_or_import_data(*args),
            data_to_upload,
            callback=segment_client._synchronize_upload_info,
            jobs=jobs,
            pbar=pbar,
        )

        return segment_client

    def get_or_create_segment(self, name: str = "default") -> FusionSegmentClient:
        """Get or create a fusion segment with the given name.

        Arguments:
            name: The name of the fusion segment.

        Returns:
            The created :class:`~tensorbay.client.segment.FusionSegmentClient` with given name.

        """
        self._status.check_authority_for_draft()
        if name not in self.list_segment_names():
            self._create_segment(name)
        return FusionSegmentClient(name, self)

    def create_segment(self, name: str = "default") -> FusionSegmentClient:
        """Create a fusion segment with the given name.

        Arguments:
            name: The name of the fusion segment.

        Returns:
            The created :class:`~tensorbay.client.segment.FusionSegmentClient` with given name.

        Raises:
            NameConflictError: When the segment exists.

        """
        self._status.check_authority_for_draft()
        if name not in self.list_segment_names():
            self._create_segment(name)
        else:
            raise NameConflictError(resource="segment", identification=name)
        return FusionSegmentClient(name, self)

    def copy_segment(
        self,
        source_name: str,
        target_name: Optional[str] = None,
        *,
        source_client: Optional["FusionDatasetClient"] = None,
        strategy: str = "abort",
    ) -> FusionSegmentClient:
        """Copy segment to this dataset.

        Arguments:
            source_name: The source name of the copied segment.
            target_name: The target name of the copied segment.
                This argument is used to specify a new name of the copied segment.
                If None, the name of the copied segment will not be changed after copy.
            source_client: The source dataset client of the copied segment.
                This argument is used to specify where the copied segment comes from when the
                copied segment is from another commit, draft or even another dataset.
                If None, the copied segment comes from this dataset.
            strategy: The strategy of handling the name conflict. There are three options:

                1. "abort": stop copying and raise exception;
                2. "override": the source segment will override the origin segment;
                3. "skip": keep the origin segment.

        Returns:
            The client of the copied target segment.

        """
        if not target_name:
            target_name = source_name
        self._copy_segment(source_name, target_name, source_client=source_client, strategy=strategy)

        return FusionSegmentClient(target_name, self)

    def move_segment(
        self,
        source_name: str,
        target_name: str,
        *,
        strategy: str = "abort",
    ) -> FusionSegmentClient:
        """Move/Rename segment in this dataset.

        Arguments:
            source_name: The source name of the moved segment.
            target_name: The target name of the moved segment.
            strategy: The strategy of handling the name conflict. There are three options:

                1. "abort": stop moving and raise exception;
                2. "override": the source segment will override the origin segment;
                3. "skip": keep the origin segment.

        Returns:
            The client of the moved target segment.

        """
        self._move_segment(source_name, target_name, strategy=strategy)
        return FusionSegmentClient(target_name, self)

    def get_segment(self, name: str = "default") -> FusionSegmentClient:
        """Get a fusion segment in a certain commit according to given name.

        Arguments:
            name: The name of the required fusion segment.

        Returns:
            The required :class:`~tensorbay.client.segment.FusionSegmentClient`.

        Raises:
            ResourceNotExistError: When the required fusion segment does not exist.

        """
        if name not in self.list_segment_names():
            raise ResourceNotExistError(resource="segment", identification=name)
        return FusionSegmentClient(name, self)

    def upload_segment(
        self,
        segment: FusionSegment,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,  # pylint: disable=unused-argument
        quiet: bool = False,
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
            quiet: Set to True to stop showing the upload process bar.

        Raises:
            Exception: When the upload got interrupted by Exception.

        Returns:
            The :class:`~tensorbay.client.segment.FusionSegmentClient`
                used for uploading the data in the segment.

        """
        self._status.check_authority_for_draft()
        try:
            with Tqdm(sum(len(frame) for frame in segment), disable=quiet) as pbar:
                return self._upload_segment(
                    segment, jobs=jobs, skip_uploaded_files=skip_uploaded_files, pbar=pbar
                )
        except Exception:
            logger.error(
                UPLOAD_SEGMENT_RESUME_TEMPLATE,
                self._status.draft_number,
                self._status.draft_number,
            )
            raise
