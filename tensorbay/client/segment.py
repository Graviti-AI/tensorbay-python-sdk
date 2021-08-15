#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""SegmentClientBase, SegmentClient and FusionSegmentClient.

The :class:`SegmentClient` is a remote concept. It
contains the information needed for determining a unique segment in a dataset
on TensorBay, and provides a series of methods within a segment scope,
such as :meth:`SegmentClient.upload_label`, :meth:`SegmentClient.upload_data`,
:meth:`SegmentClient.list_data` and so on.
In contrast to the :class:`SegmentClient`,
:class:`~tensorbay.dataset.segment.Segment` is a local concept.
It represents a segment created locally. Please refer to
:class:`~tensorbay.dataset.segment.Segment` for more information.

Similarly to the :class:`SegmentClient`, the :class:`FusionSegmentClient` represents
the fusion segment in a fusion dataset on TensorBay, and its local counterpart
is :class:`~tensorbay.dataset.segment.FusionSegment`.
Please refer to :class:`~tensorbay.dataset.segment.FusionSegment`
for more information.

"""

import time
from copy import deepcopy
from itertools import zip_longest
from typing import TYPE_CHECKING, Any, Callable, Dict, Generator, Iterable, Optional, Tuple, Union

import filetype
from requests_toolbelt import MultipartEncoder
from ulid import from_timestamp

from ..dataset import AuthData, Data, Frame, RemoteData
from ..exception import FrameError, InvalidParamsError, OperationError
from ..label import Label
from ..sensor.sensor import Sensor, Sensors
from ..utility import Disable, FileMixin, chunked, locked
from .lazy import PagingList
from .requests import config
from .status import Status

if TYPE_CHECKING:
    from .dataset import DatasetClient, FusionDatasetClient

_STRATEGIES = {"abort", "override", "skip"}
_MASK_KEYS = ("semantic_mask", "instance_mask", "panoptic_mask")


class _UrlGetters:
    def __init__(self, urls: PagingList[str]) -> None:
        self._urls = urls

    def __getitem__(self, index: int) -> Callable[[str], str]:
        return lambda _: self._urls[index]


class SegmentClientBase:  # pylint: disable=too-many-instance-attributes
    """This class defines the basic concept of :class:`SegmentClient`.

    A :class:`SegmentClientBase` contains the information needed for determining
        a unique segment in a dataset on TensorBay.

    Arguments:
        name: Segment name.
        dataset_client: The dataset client.

    Attributes:
        name: Segment name.
        status: The status of the dataset client.

    """

    _EXPIRED_IN_SECOND = 240

    def __init__(
        self, name: str, dataset_client: "Union[DatasetClient, FusionDatasetClient]"
    ) -> None:

        self._name = name
        self._dataset_id = dataset_client.dataset_id
        self._dataset_client = dataset_client
        self._status = dataset_client.status
        self._client = dataset_client._client  # pylint: disable=protected-access
        self._permission: Dict[str, Any] = {"expireAt": 0}

    def _get_url(self, remote_path: str) -> str:
        """Get URL of a specific remote path.

        Arguments:
            remote_path: The remote path of the file.

        Returns:
            The URL of the remote file.

        """
        params: Dict[str, Any] = {
            "segmentName": self._name,
            "remotePath": remote_path,
        }
        params.update(self._status.get_status_info())

        if config.is_internal:
            params["isInternal"] = True

        response = self._client.open_api_do("GET", "data/urls", self._dataset_id, params=params)
        return response.json()["urls"][0]["url"]  # type: ignore[no-any-return]

    def _list_urls(self, offset: int = 0, limit: int = 128) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "segmentName": self._name,
            "offset": offset,
            "limit": limit,
        }
        params.update(self._status.get_status_info())

        if config.is_internal:
            params["isInternal"] = True

        response = self._client.open_api_do("GET", "data/urls", self._dataset_id, params=params)
        return response.json()  # type: ignore[no-any-return]

    def _list_mask_urls(self, mask_type: str, offset: int = 0, limit: int = 128) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "segmentName": self._name,
            "maskType": mask_type,
            "offset": offset,
            "limit": limit,
        }
        params.update(self._status.get_status_info())

        if config.is_internal:
            params["isInternal"] = True

        response = self._client.open_api_do("GET", "masks/urls", self._dataset_id, params=params)
        return response.json()  # type: ignore[no-any-return]

    def _list_labels(self, offset: int = 0, limit: int = 128) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "segmentName": self._name,
            "offset": offset,
            "limit": limit,
        }
        params.update(self._status.get_status_info())

        response = self._client.open_api_do("GET", "labels", self._dataset_id, params=params)
        return response.json()  # type: ignore[no-any-return]

    @locked
    def _request_upload_permission(self) -> None:
        params: Dict[str, Any] = {"expired": self._EXPIRED_IN_SECOND, "segmentName": self._name}
        params.update(self._status.get_status_info())

        if config.is_internal:
            params["isInternal"] = True

        self._permission = self._client.open_api_do(
            "GET", "policies", self._dataset_id, params=params
        ).json()

        del self._permission["result"]["multipleUploadLimit"]

    def _get_upload_permission(self) -> Dict[str, Any]:
        if int(time.time()) >= self._permission["expireAt"]:
            self._request_upload_permission()

        return deepcopy(self._permission)

    def _upload_file(self, data: FileMixin) -> None:
        """Upload the file in the data to the draft.

        Arguments:
            data: The data instance needs to be uploaded.

        """
        permission = self._get_upload_permission()
        post_data = permission["result"]

        local_path = data.path
        checksum = data.get_checksum()

        post_data["key"] = permission["extra"]["objectPrefix"] + checksum

        backend_type = permission["extra"]["backendType"]
        if backend_type == "azure":
            url = (
                f'{permission["extra"]["host"]}{permission["extra"]["objectPrefix"]}'
                f'{checksum}?{permission["result"]["token"]}'
            )

            self._put_binary_file_to_azure(url, local_path, post_data)
        else:
            self._post_multipart_formdata(
                permission["extra"]["host"],
                local_path,
                post_data,
            )

    def _upload_mask_files(self, label: Label) -> None:
        for key in _MASK_KEYS:
            mask = getattr(label, key, None)
            if mask:
                self._upload_file(mask)

    def _post_multipart_formdata(
        self,
        url: str,
        local_path: str,
        data: Dict[str, Any],
    ) -> None:
        with open(local_path, "rb") as fp:
            file_type = filetype.guess_mime(local_path)
            if "x-amz-date" in data:
                data["Content-Type"] = file_type
            data["file"] = ("", fp, file_type)
            multipart = MultipartEncoder(data)

            self._client.do(
                "POST", url, data=multipart, headers={"Content-Type": multipart.content_type}
            )

    def _put_binary_file_to_azure(
        self,
        url: str,
        local_path: str,
        data: Dict[str, Any],
    ) -> None:
        with open(local_path, "rb") as fp:
            file_type = filetype.guess_mime(local_path)
            request_headers = {
                "x-ms-blob-content-type": file_type,
                "x-ms-blob-type": data["x-ms-blob-type"],
            }
            self._client.do("PUT", url, data=fp, headers=request_headers)

    def _synchronize_upload_info(
        self,
        callback_bodies: Tuple[Dict[str, Any], ...],
    ) -> None:
        put_data: Dict[str, Any] = {
            "segmentName": self.name,
            "objects": callback_bodies,
        }
        put_data.update(self._status.get_status_info())

        self._client.open_api_do("PUT", "multi/callback", self._dataset_id, json=put_data)

    def _import_cloud_file(
        self,
        cloud_path: str,
        remote_path: str,
    ) -> None:

        put_data: Dict[str, Any] = {
            "segmentName": self.name,
            "objects": [{"cloudPath": cloud_path, "remotePath": remote_path}],
            "deleteSource": False,
        }
        put_data.update(self._status.get_status_info())
        self._client.open_api_do("PUT", "multi/cloud-callback", self._dataset_id, json=put_data)

    def _upload_label(self, data: Union[AuthData, Data]) -> None:
        label = data.label.dumps()
        if not label:
            return

        post_data: Dict[str, Any] = {
            "segmentName": self.name,
            "remotePath": data.target_remote_path,
            "label": label,
        }
        post_data.update(self._status.get_status_info())

        self._client.open_api_do("PUT", "labels", self._dataset_id, json=post_data)

    @property
    def name(self) -> str:
        """Return the segment name.

        Returns:
            The segment name.

        """
        return self._name

    @property
    def status(self) -> Status:
        """Return the status of the dataset client.

        Returns:
            The status of the dataset client.

        """
        return self._status

    @Disable(since="v1.6.0", enabled_in="v1.11.0", reason="TensorBay server refactor")
    def delete_data(self, remote_paths: Union[str, Iterable[str]]) -> None:
        """Delete data of a segment in a certain commit with the given remote paths.

        Arguments:
            remote_paths: The remote paths of data in a segment.

        """
        self._status.check_authority_for_draft()

        all_paths = iter((remote_paths,)) if isinstance(remote_paths, str) else iter(remote_paths)

        for request_remote_paths in chunked(all_paths, 128):
            delete_data: Dict[str, Any] = {
                "segmentName": self.name,
                "remotePaths": request_remote_paths,
            }
            delete_data.update(self._status.get_status_info())

            self._client.open_api_do("DELETE", "data", self._dataset_id, json=delete_data)


class SegmentClient(SegmentClientBase):
    """This class defines :class:`SegmentClient`.

    :class:`SegmentClient` inherits from SegmentClientBase and provides methods within a
    segment scope, such as `upload_label()`, `upload_data()`, `list_data()` and so on.
    In contrast to FusionSegmentClient, :class:`SegmentClient` has only one sensor.

    """

    _dataset_client: "DatasetClient"

    def __init__(self, name: str, data_client: "DatasetClient") -> None:
        super().__init__(name, data_client)

    def _generate_data_paths(self, offset: int = 0, limit: int = 128) -> Generator[str, None, int]:
        params: Dict[str, Any] = {
            "segmentName": self._name,
            "offset": offset,
            "limit": limit,
        }
        params.update(self._status.get_status_info())

        response = self._client.open_api_do("GET", "data", self._dataset_id, params=params).json()

        for item in response["data"]:
            yield item["remotePath"]

        return response["totalCount"]  # type: ignore[no-any-return]

    def _generate_data(
        self, url_getters: Dict[str, _UrlGetters], offset: int = 0, limit: int = 128
    ) -> Generator[RemoteData, None, int]:
        response = self._list_labels(offset, limit)
        urls = url_getters["file"]

        for i, item in enumerate(response["labels"], offset):
            data = RemoteData.from_response_body(item, _url_getter=urls[i])
            label = data.label
            for key in _MASK_KEYS:
                mask = getattr(label, key, None)
                if mask:
                    # pylint: disable=protected-access
                    mask._url_getter = url_getters[key][i]

            yield data

        return response["totalCount"]  # type: ignore[no-any-return]

    def _generate_urls(self, offset: int = 0, limit: int = 128) -> Generator[str, None, int]:
        response = self._list_urls(offset, limit)

        for item in response["urls"]:
            yield item["url"]

        return response["totalCount"]  # type: ignore[no-any-return]

    def _generate_mask_urls(
        self, mask_type: str, offset: int = 0, limit: int = 128
    ) -> Generator[str, None, int]:
        response = self._list_mask_urls(mask_type, offset, limit)

        for item in response["urls"]:
            yield item["url"]

        return response["totalCount"]  # type: ignore[no-any-return]

    def _upload_or_import_data(self, data: Union[Data, AuthData]) -> Optional[Dict[str, Any]]:
        if isinstance(data, Data):
            self._upload_file(data)
            self._upload_mask_files(data.label)
            return data.get_callback_body()

        self.import_auth_data(data)
        return None

    def upload_file(self, local_path: str, target_remote_path: str = "") -> None:
        """Upload data with local path to the draft.

        Arguments:
            local_path: The local path of the data to upload.
            target_remote_path: The path to save the data in segment client.

        """
        self._status.check_authority_for_draft()

        data = Data(local_path, target_remote_path=target_remote_path)
        self._upload_file(data)

        self._synchronize_upload_info((data.get_callback_body(),))

    def upload_label(self, data: Data) -> None:
        """Upload label with Data object to the draft.

        Arguments:
            data: The data object which represents the local file to upload.

        """
        self._status.check_authority_for_draft()

        self._upload_mask_files(data.label)
        self._upload_label(data)

    def upload_data(self, data: Data) -> None:
        """Upload Data object to the draft.

        Arguments:
            data: The :class:`~tensorbay.dataset.data.Data`.

        """
        self._status.check_authority_for_draft()
        self._upload_file(data)
        self._upload_mask_files(data.label)
        self._synchronize_upload_info((data.get_callback_body(),))

    def import_auth_data(self, data: AuthData) -> None:
        """Import AuthData object to the draft.

        Arguments:
            data: The :class:`~tensorbay.dataset.data.Data`.

        """
        self._status.check_authority_for_draft()

        self._import_cloud_file(data.path, data.target_remote_path)
        self._upload_label(data)

    def copy_data(
        self,
        source_remote_paths: Union[str, Iterable[str]],
        target_remote_paths: Union[None, str, Iterable[str]] = None,
        *,
        source_client: Optional["SegmentClient"] = None,
        strategy: str = "abort",
    ) -> None:
        """Copy data to this segment.

        Arguments:
            source_remote_paths: The source remote paths of the copied data.
            target_remote_paths: The target remote paths of the copied data.
                This argument is used to specify new remote paths of the copied data.
                If None, the remote path of the copied data will not be changed after copy.
            source_client: The source segment client of the copied data.
                This argument is used to specifies where the copied data comes from when the copied
                data is from another commit, draft, segment or even another dataset.
                If None, the copied data comes from this segment.
            strategy: The strategy of handling the name conflict. There are three options:

                1. "abort": stop copying and raise exception;
                2. "override": the source data will override the origin data;
                3. "skip": keep the origin data.

        Raises:
            InvalidParamsError: When strategy is invalid.
            OperationError: When the type of target_remote_paths is not equal
                with source_remote_paths.

        """
        self._status.check_authority_for_draft()

        if strategy not in _STRATEGIES:
            raise InvalidParamsError(param_name="strategy", param_value=strategy)

        if not target_remote_paths:
            all_target_remote_paths = []
            all_source_remote_paths = (
                [source_remote_paths]
                if isinstance(source_remote_paths, str)
                else list(source_remote_paths)
            )

        elif isinstance(source_remote_paths, str) and isinstance(target_remote_paths, str):
            all_target_remote_paths = [target_remote_paths]
            all_source_remote_paths = [source_remote_paths]

        elif not isinstance(source_remote_paths, str) and not isinstance(target_remote_paths, str):
            all_target_remote_paths = list(target_remote_paths)
            all_source_remote_paths = list(source_remote_paths)
            if len(all_target_remote_paths) != len(all_source_remote_paths):
                raise OperationError(
                    "To copy the data, the length of target_remote_paths "
                    "must be equal with source_remote_paths"
                )
        else:
            raise OperationError(
                "To copy the data, the type of target_remote_paths "
                "must be equal with source_remote_paths"
            )

        source = {}
        if source_client:
            source["segmentName"] = source_client.name
            source["id"] = source_client._dataset_id  # pylint: disable=protected-access
            source.update(source_client.status.get_status_info())
        else:
            source["segmentName"] = self.name

        post_data: Dict[str, Any] = {
            "strategy": strategy,
            "source": source,
            "segmentName": self.name,
        }
        post_data.update(self._status.get_status_info())

        for targets, sources in zip_longest(
            chunked(all_target_remote_paths, 128), chunked(all_source_remote_paths, 128)
        ):
            if targets:
                post_data["remotePaths"] = targets
            post_data["source"]["remotePaths"] = sources

            self._client.open_api_do("POST", "data?multipleCopy", self._dataset_id, json=post_data)

    def move_data(
        self,
        source_remote_paths: Union[str, Iterable[str]],
        target_remote_paths: Union[None, str, Iterable[str]] = None,
        *,
        source_client: Optional["SegmentClient"] = None,
        strategy: str = "abort",
    ) -> None:
        """Move data to this segment, also used to rename data.

        Arguments:
            source_remote_paths: The source remote paths of the moved data.
            target_remote_paths: The target remote paths of the moved data.
                This argument is used to specify new remote paths of the moved data.
                If None, the remote path of the moved data will not be changed after copy.
            source_client: The source segment client of the moved data.
                This argument is used to specifies where the moved data comes from when the moved
                data is from another segment.
                If None, the moved data comes from this segment.
            strategy: The strategy of handling the name conflict. There are three options:

                1. "abort": stop copying and raise exception;
                2. "override": the source data will override the origin data;
                3. "skip": keep the origin data.

        Raises:
            InvalidParamsError: When strategy is invalid.
            OperationError: When the type or the length of target_remote_paths is not equal
                with source_remote_paths.
                Or when the dataset_id and drafter_number of source_client
                is not equal with the current segment client.

        """
        self._status.check_authority_for_draft()

        if strategy not in _STRATEGIES:
            raise InvalidParamsError(param_name="strategy", param_value=strategy)

        if not target_remote_paths:
            all_target_remote_paths = []
            all_source_remote_paths = (
                [source_remote_paths]
                if isinstance(source_remote_paths, str)
                else list(source_remote_paths)
            )

        elif isinstance(source_remote_paths, str) and isinstance(target_remote_paths, str):
            all_target_remote_paths = [target_remote_paths]
            all_source_remote_paths = [source_remote_paths]

        elif not isinstance(source_remote_paths, str) and not isinstance(target_remote_paths, str):
            all_target_remote_paths = list(target_remote_paths)
            all_source_remote_paths = list(source_remote_paths)
            if len(all_target_remote_paths) != len(all_source_remote_paths):
                raise OperationError(
                    "To move the data, the length of target_remote_paths "
                    "must be equal with source_remote_paths"
                )
        else:
            raise OperationError(
                "To move the data, the type of target_remote_paths "
                "must be equal with source_remote_paths"
            )

        source = {}
        if source_client:
            if (
                source_client.status.draft_number == self.status.draft_number
                and source_client._dataset_id  # pylint: disable=protected-access
                == self._dataset_id  # pylint: disable=protected-access
            ):
                source["segmentName"] = source_client.name
            else:
                raise OperationError(
                    "To move the data, the dataset_id and drafter_number of source_client "
                    "must be equal with the current segment client"
                )
        else:
            source["segmentName"] = self.name

        post_data: Dict[str, Any] = {
            "strategy": strategy,
            "source": source,
            "segmentName": self.name,
        }
        post_data.update(self._status.get_status_info())

        for targets, sources in zip_longest(
            chunked(all_target_remote_paths, 128), chunked(all_source_remote_paths, 128)
        ):
            if targets:
                post_data["remotePaths"] = targets
            post_data["source"]["remotePaths"] = sources

            self._client.open_api_do("POST", "data?multipleMove", self._dataset_id, json=post_data)

    def list_data_paths(self) -> PagingList[str]:
        """List required data path in a segment in a certain commit.

        Returns:
            The PagingList of data paths.

        """
        return PagingList(self._generate_data_paths, 128)

    def list_data(self) -> PagingList[RemoteData]:
        """List required Data object in a dataset segment.

        Returns:
            The PagingList of :class:`~tensorbay.dataset.data.RemoteData`.

        """
        url_getters = {"file": _UrlGetters(self.list_urls())}
        for key in _MASK_KEYS:
            url_getters[key] = _UrlGetters(self.list_mask_urls(key.upper()))

        return PagingList(
            lambda offset, limit: self._generate_data(url_getters, offset, limit), 128
        )

    def list_urls(self) -> PagingList[str]:
        """List the data urls in this segment.

        Returns:
            The PagingList of urls.

        """
        return PagingList(self._generate_urls, 128)

    def list_mask_urls(self, mask_type: str) -> PagingList[str]:
        """List the mask urls in this segment.

        Arguments:
            mask_type: The required mask type, the supported types are
                ``SEMANTIC_MASK``, ``INSTANCE_MASK`` and ``PANOPTIC_MASK``

        Returns:
            The PagingList of mask urls.

        """
        return PagingList(
            lambda offset, limit: self._generate_mask_urls(mask_type, offset, limit), 128
        )


class FusionSegmentClient(SegmentClientBase):
    """This class defines :class:`FusionSegmentClient`.

    :class:`FusionSegmentClient` inherits from :class:`SegmentClientBase` and provides
    methods within a fusion segment scope, such as
    :meth:`FusionSegmentClient.upload_sensor`,
    :meth:`FusionSegmentClient.upload_frame`
    and :meth:`FusionSegmentClient.list_frames`.

    In contrast to :class:`SegmentClient`, :class:`FusionSegmentClient` has multiple sensors.

    """

    _dataset_client: "FusionDatasetClient"

    def __init__(self, name: str, data_client: "FusionDatasetClient") -> None:
        super().__init__(name, data_client)

    def _generate_frames(
        self, urls: PagingList[Dict[str, str]], offset: int = 0, limit: int = 128
    ) -> Generator[Frame, None, int]:
        response = self._list_labels(offset, limit)

        for index, item in enumerate(response["labels"], offset):
            yield Frame.from_response_body(item, index, urls)

        return response["totalCount"]  # type: ignore[no-any-return]

    def _generate_urls(
        self, offset: int = 0, limit: int = 128
    ) -> Generator[Dict[str, str], None, int]:
        response = self._list_urls(offset, limit)

        for frame in response["urls"]:
            yield {item["sensorName"]: item["url"] for item in frame["urls"]}

        return response["totalCount"]  # type: ignore[no-any-return]

    def _upload_or_import_data(
        self,
        data: Union[Data, AuthData],
        sensor_name: str,
        frame_id: str,
    ) -> Optional[Dict[str, Any]]:
        if isinstance(data, Data):
            self._upload_file(data)
            self._upload_mask_files(data.label)

            callback_body = data.get_callback_body()
            callback_body["frameId"] = frame_id
            callback_body["sensorName"] = sensor_name
            return callback_body
        return None

    def get_sensors(self) -> Sensors:
        """Return the sensors in a fusion segment client.

        Returns:
            The :class:`sensors<~tensorbay.sensor.sensor.Sensors>` in the fusion segment client.

        """
        params: Dict[str, Any] = {"segmentName": self._name}
        params.update(self._status.get_status_info())

        response = self._client.open_api_do(
            "GET", "sensors", self._dataset_id, params=params
        ).json()

        return Sensors.loads(response["sensors"])

    def upload_sensor(self, sensor: Sensor) -> None:
        """Upload sensor to the draft.

        Arguments:
            sensor: The sensor to upload.

        """
        self._status.check_authority_for_draft()

        post_data = sensor.dumps()
        post_data.update(self._status.get_status_info())

        post_data["segmentName"] = self._name
        self._client.open_api_do("POST", "sensors", self._dataset_id, json=post_data)

    def delete_sensor(self, sensor_name: str) -> None:
        """Delete a TensorBay sensor of the draft with the given sensor name.

        Arguments:
            sensor_name: The TensorBay sensor to delete.

        """
        self._status.check_authority_for_draft()

        delete_data: Dict[str, Any] = {"segmentName": self._name, "sensorName": sensor_name}
        delete_data.update(self._status.get_status_info())

        self._client.open_api_do("DELETE", "sensors", self._dataset_id, json=delete_data)

    def upload_frame(self, frame: Frame, timestamp: Optional[float] = None) -> None:
        """Upload frame to the draft.

        Arguments:
            frame: The :class:`~tensorbay.dataset.frame.Frame` to upload.
            timestamp: The mark to sort frames, supporting timestamp and float.

        Raises:
            FrameError: When lacking frame id or frame id conflicts.

        """
        self._status.check_authority_for_draft()

        if timestamp is None:
            try:
                frame_id = frame.frame_id
            except AttributeError as error:
                raise FrameError(
                    "Lack frame id, please add frame id in frame or "
                    "give timestamp to the function!"
                ) from error
        elif not hasattr(frame, "frame_id"):
            frame_id = from_timestamp(timestamp)
        else:
            raise FrameError("Frame id conflicts, please do not give timestamp to the function!.")

        callback_bodies = []
        for sensor_name, data in frame.items():
            if not isinstance(data, Data):
                continue

            self._upload_file(data)
            self._upload_mask_files(data.label)

            callback_body = data.get_callback_body()
            callback_body["frameId"] = frame_id.str
            callback_body["sensorName"] = sensor_name
            callback_bodies.append(callback_body)

        for chunked_callback_bodies in chunked(callback_bodies, 50):
            self._synchronize_upload_info(chunked_callback_bodies)

    def list_frames(self) -> PagingList[Frame]:
        """List required frames in the segment in a certain commit.

        Returns:
            The PagingList of :class:`~tensorbay.dataset.frame.Frame`.

        """
        urls = self.list_urls()
        return PagingList(lambda offset, limit: self._generate_frames(urls, offset, limit), 128)

    def list_urls(self) -> PagingList[Dict[str, str]]:
        """List the data urls in this segment.

        Returns:
            The PagingList of url dict, which key is the sensor name, value is the url.

        """
        urls = PagingList(self._generate_urls, 128)
        urls._repr_maxlevel = 2  # pylint: disable=protected-access
        return urls
