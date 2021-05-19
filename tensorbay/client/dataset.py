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

from ..dataset import Data, Frame, FusionSegment, Notes, Segment
from ..exception import FrameError, NameConflictError, ResourceNotExistError
from ..label import Catalog
from .commit_status import CommitStatus
from .log import UPLOAD_SEGMENT_RESUME_TEMPLATE
from .requests import Client, PagingList, Tqdm, multithread_upload
from .segment import FusionSegmentClient, SegmentClient
from .struct import Branch, Commit, Draft, Tag

if TYPE_CHECKING:
    from .gas import GAS

logger = logging.getLogger(__name__)


class DatasetClientBase:  # pylint: disable=too-many-public-methods
    """This class defines the basic concept of the dataset client.

    A :class:`DatasetClientBase` contains the information needed for
    determining a unique dataset on TensorBay, and provides a series of
    method within dataset scope, such as :meth:`DatasetClientBase.list_segment_names`
    and :meth:`DatasetClientBase.upload_catalog`.

    Arguments:
        name: Dataset name.
        dataset_id: Dataset ID.
        gas_client: The initial client to interact between local and TensorBay.

    Attributes:
        name: Dataset name.
        dataset_id: Dataset ID.
        status: The status of the dataset client.

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
            self._status.checkout(commit_id=commit_id)

    def _commit(self, message: str, tag: Optional[str] = None) -> str:
        post_data: Dict[str, Any] = {
            "message": message,
        }
        post_data.update(self._status.get_status_info())

        if tag:
            post_data["tag"] = tag

        response = self._client.open_api_do("POST", "commits", self.dataset_id, json=post_data)
        return response.json()["commitId"]  # type: ignore[no-any-return]

    def _create_draft(self, title: Optional[str] = None) -> int:
        post_data: Dict[str, Any] = {}

        if title:
            post_data["title"] = title

        response = self._client.open_api_do("POST", "drafts", self.dataset_id, json=post_data)
        return response.json()["draftNumber"]  # type: ignore[no-any-return]

    def _generate_drafts(self, offset: int = 0, limit: int = 128) -> Generator[Draft, None, int]:
        params = {"offset": offset, "limit": limit}
        response = self._client.open_api_do("GET", "drafts", self.dataset_id, params=params).json()

        for item in response["drafts"]:
            yield Draft.loads(item)

        return response["totalCount"]  # type: ignore[no-any-return]

    def _generate_commits(
        self, revision: Optional[str] = None, offset: int = 0, limit: int = 128
    ) -> Generator[Commit, None, int]:
        params: Dict[str, Any] = {"offset": offset, "limit": limit}
        if revision:
            params["commit"] = revision

        response = self._client.open_api_do("GET", "commits", self.dataset_id, params=params).json()

        for item in response["commits"]:
            yield Commit.loads(item)

        return response["totalCount"]  # type: ignore[no-any-return]

    def _generate_tags(
        self, name: Optional[str] = None, offset: int = 0, limit: int = 128
    ) -> Generator[Tag, None, int]:
        params: Dict[str, Any] = {"offset": offset, "limit": limit}
        if name:
            params["name"] = name

        response = self._client.open_api_do("GET", "tags", self.dataset_id, params=params).json()

        for item in response["tags"]:
            yield Tag.loads(item)

        return response["totalCount"]  # type: ignore[no-any-return]

    def _generate_branches(
        self, name: Optional[str] = None, offset: int = 0, limit: int = 128
    ) -> Generator[Branch, None, int]:
        params: Dict[str, Any] = {"offset": offset, "limit": limit}
        if name:
            params["name"] = name

        response = self._client.open_api_do(
            "GET", "branches", self.dataset_id, params=params
        ).json()

        for item in response["branches"]:
            yield Branch.loads(item)

        return response["totalCount"]  # type: ignore[no-any-return]

    def _create_segment(self, name: str) -> None:
        post_data: Dict[str, Any] = {"name": name}
        post_data.update(self._status.get_status_info())

        self._client.open_api_do("POST", "segments", self.dataset_id, json=post_data)

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
            The draft number of the created draft.

        """
        self._status.check_authority_for_commit()
        draft_number = self._create_draft(title)
        self._status.checkout(draft_number=draft_number)
        return draft_number

    def get_draft(self, draft_number: Optional[int] = None) -> Draft:
        """Get the certain draft with the given draft number.

        Arguments:
            draft_number: The required draft number.
                If is not given, get the current draft.

        Returns:
            The :class:`.Draft` instance with the given number.

        Raises:
            TypeError: When the given draft number is illegal.
            ResourceNotExistError: When the required draft does not exist.

        """
        if draft_number is None:
            self._status.check_authority_for_draft()
            draft_number = self._status.draft_number

        if not draft_number:
            raise TypeError("The given draft number is illegal")

        for draft in self.list_drafts():
            if draft_number == draft.number:
                return draft

        raise ResourceNotExistError(resource="draft", identification=draft_number)

    def list_drafts(self) -> PagingList[Draft]:
        """List all the drafts.

        Returns:
            The PagingList of :class:`drafts<.Draft>`.

        """
        return PagingList(self._generate_drafts, 128)

    def get_commit(self, revision: Optional[str] = None) -> Commit:
        """Get the certain commit with the given revision.

        Arguments:
            revision: The information to locate the specific commit, which can be the commit id,
                the branch name, or the tag name.
                If is not given, get the current commit.

        Returns:
            The :class:`.Commit` instance with the given revision.

        Raises:
            TypeError: When the given revision is illegal.
            ResourceNotExistError: When the required commit does not exist.

        """
        if revision is None:
            self._status.check_authority_for_commit()
            revision = self._status.commit_id

        if not revision:
            raise TypeError("The given revision is illegal")

        try:
            commit = next(self._generate_commits(revision))
        except StopIteration as error:
            raise ResourceNotExistError(resource="commit", identification=revision) from error

        return commit

    def list_commits(self, revision: Optional[str] = None) -> PagingList[Commit]:
        """List the commits.

        Arguments:
            revision: The information to locate the specific commit, which can be the commit id,
                the branch name, or the tag name.
                If is given, list the commits before the given commit.
                If is not given, list the commits before the current commit.

        Returns:
            The PagingList of :class:`commits<.Commit>`.

        """
        return PagingList(
            lambda offset, limit: self._generate_commits(revision, offset, limit), 128
        )

    def create_tag(self, name: str, revision: Optional[str] = None) -> None:
        """Create the tag for a commit.

        Arguments:
            name: The tag name to be created for the specific commit.
            revision: The information to locate the specific commit, which can be the commit id,
                the branch name, or the tag name.
                If the revision is not given, create the tag for the current commit.

        """
        if not revision:
            self._status.check_authority_for_commit()
            revision = self._status.commit_id

        post_data: Dict[str, Any] = {"commit": revision, "name": name}

        self._client.open_api_do("POST", "tags", self.dataset_id, json=post_data)

    def get_tag(self, name: str) -> Tag:
        """Get the certain tag with the given name.

        Arguments:
            name: The required tag name.

        Returns:
            The :class:`.Tag` instance with the given name.

        Raises:
            TypeError: When the given tag is illegal.
            ResourceNotExistError: When the required tag does not exist.

        """
        if not name:
            raise TypeError("The given tag name is illegal")

        try:
            tag = next(self._generate_tags(name))
        except StopIteration as error:
            raise ResourceNotExistError(resource="tag", identification=name) from error

        return tag

    def list_tags(self) -> PagingList[Tag]:
        """List the information of tags.

        Returns:
            The PagingList of :class:`tags<.Tag>`.

        """
        return PagingList(lambda offset, limit: self._generate_tags(None, offset, limit), 128)

    def get_branch(self, name: str) -> Branch:
        """Get the branch with the given name.

        Arguments:
            name: The required branch name.

        Returns:
            The :class:`.Branch` instance with the given name.

        Raises:
            TypeError: When the given branch is illegal.
            ResourceNotExistError: When the required branch does not exist.

        """
        if not name:
            raise TypeError("The given branch name is illegal")

        try:
            branch = next(self._generate_branches(name))
        except StopIteration as error:
            raise ResourceNotExistError(resource="branch", identification=name) from error

        return branch

    def list_branches(self) -> PagingList[Branch]:
        """List the information of branches.

        Returns:
            The PagingList of :class:`branches<.Branch>`.

        """
        return PagingList(lambda offset, limit: self._generate_branches(None, offset, limit), 128)

    def checkout(self, revision: Optional[str] = None, draft_number: Optional[int] = None) -> None:
        """Checkout to commit or draft.

        Arguments:
            revision: The information to locate the specific commit, which can be the commit id,
                the branch, or the tag.
            draft_number: The draft number.

        Raises:
            TypeError: When both commit and draft number are provided or neither.

        """
        if revision is None and draft_number is None:
            raise TypeError("Neither revision nor draft number is given, please give one")
        if revision is not None and draft_number is not None:
            raise TypeError("Both revision and draft number are given, please only give one")

        if revision:
            commit_id = self.get_commit(revision).commit_id
            self._status.checkout(commit_id=commit_id)

        if draft_number:
            draft_number = self.get_draft(draft_number).number
            self._status.checkout(draft_number=draft_number)

    def commit(self, message: str, *, tag: Optional[str] = None) -> None:
        """Commit the draft.

        Arguments:
            message: The commit message.
            tag: A tag for current commit.

        """
        self._status.check_authority_for_draft()
        self._status.checkout(commit_id=self._commit(message, tag))

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

        self._client.open_api_do("PATCH", "notes", self.dataset_id, json=patch_data)

    def get_notes(self) -> Notes:
        """Get the notes.

        Returns:
            The :class:`~tensorbay.dataset.dataset.Notes`.

        """
        params: Dict[str, Any] = self._status.get_status_info()

        return Notes.loads(
            self._client.open_api_do("GET", "notes", self.dataset_id, params=params).json()
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

    def delete_tag(self, name: str) -> None:
        """Delete a tag.

        Arguments:
            name: The tag name to be deleted for the specific commit.

        """
        delete_data: Dict[str, Any] = {"name": name}

        self._client.open_api_do("DELETE", "tags", self.dataset_id, json=delete_data)

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
        local_data: Iterator[Data] = filter(
            lambda data: pbar.update_for_skip(isinstance(data, Data)),
            segment,  # type: ignore[arg-type]
        )
        if skip_uploaded_files:
            done_set = set(segment_client.list_data_paths())
            segment_filter = filter(
                lambda data: pbar.update_for_skip(data.target_remote_path not in done_set),
                local_data,
            )
        else:
            segment_filter = local_data

        multithread_upload(segment_client.upload_data, segment_filter, jobs=jobs, pbar=pbar)

        return segment_client

    def get_or_create_segment(self, name: str = "") -> SegmentClient:
        """Get or create a segment with the given name.

        Arguments:
            name: Segment name, can not be "_default".

        Returns:
            The created :class:`~tensorbay.client.segment.SegmentClient` with given name.

        """
        self._status.check_authority_for_draft()
        if name not in self.list_segment_names():
            self._create_segment(name)
        return SegmentClient(name, self)

    def create_segment(self, name: str = "") -> SegmentClient:
        """Create a segment with the given name.

        Arguments:
            name: Segment name, can not be "_default".

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

    def get_segment(self, name: str = "") -> SegmentClient:
        """Get a segment in a certain commit according to given name.

        Arguments:
            name: The name of the required segment.

        Returns:
            The required class:`~tensorbay.client.segment.SegmentClient`.

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
                    segment, jobs=jobs, skip_uploaded_files=skip_uploaded_files, pbar=pbar
                )
        except Exception:
            logger.error(
                UPLOAD_SEGMENT_RESUME_TEMPLATE,
                self._status.draft_number,
                self._status.draft_number,
            )
            raise


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
    def _skip_upload_frame(
        segment_filter: Iterator[Tuple[Frame, Optional[int], bool]],
        done_set: Dict[float, Frame],
        pbar: Tqdm,
    ) -> Iterator[Tuple[Frame, Optional[int], bool]]:
        for frame, timestamp, _ in segment_filter:
            if timestamp is None:
                timestamp = frame.frame_id.timestamp().timestamp
            remote_frame = done_set.get(timestamp)
            if remote_frame is None:
                yield frame, timestamp, False
            elif len(frame) != len(remote_frame):
                frame.frame_id = remote_frame.frame_id
                yield frame, None, True
            else:
                pbar.update()

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
        for sensor in segment.sensors.values():
            segment_client.upload_sensor(sensor)

        segment_filter: Iterator[Tuple[Frame, Optional[int], bool]]

        if not segment:
            return segment_client

        have_frame_id = hasattr(segment[0], "frame_id")

        for frame in segment:
            if not hasattr(frame, "frame_id") == have_frame_id:
                raise FrameError(
                    "All the frames should have the same patterns(all have frame id or not)."
                )

        if have_frame_id:
            segment_filter = ((frame, None, False) for frame in segment)
        else:
            segment_filter = (
                (frame, 10 * index + 10, False) for index, frame in enumerate(segment)
            )

        if skip_uploaded_files:
            done_set = {
                frame.frame_id.timestamp().timestamp: frame
                for frame in segment_client.list_frames()
            }
            segment_filter = self._skip_upload_frame(segment_filter, done_set, pbar)

        multithread_upload(
            lambda args: segment_client.upload_frame(*args),
            segment_filter,
            jobs=jobs,
            pbar=pbar,
        )

        return segment_client

    def get_or_create_segment(self, name: str = "") -> FusionSegmentClient:
        """Get or create a fusion segment with the given name.

        Arguments:
            name: Segment name, can not be "_default".

        Returns:
            The created :class:`~tensorbay.client.segment.FusionSegmentClient` with given name.

        """
        self._status.check_authority_for_draft()
        if name not in self.list_segment_names():
            self._create_segment(name)
        return FusionSegmentClient(name, self)

    def create_segment(self, name: str = "") -> FusionSegmentClient:
        """Create a fusion segment with the given name.

        Arguments:
            name: Segment name, can not be "_default".

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

    def get_segment(self, name: str = "") -> FusionSegmentClient:
        """Get a fusion segment in a certain commit according to given name.

        Arguments:
            name: The name of the required fusion segment.

        Returns:
            The required class:`~tensorbay.client.segment.FusionSegmentClient`.

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
            with Tqdm(len(segment), disable=quiet) as pbar:
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
