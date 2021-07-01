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

import os
import time
from copy import deepcopy
from hashlib import sha1
from itertools import islice
from typing import TYPE_CHECKING, Any, Dict, Generator, Iterable, List, Optional, Union

import filetype
from requests_toolbelt import MultipartEncoder
from ulid import from_timestamp

from ..dataset import AuthData, Data, Frame, RemoteData
from ..exception import FrameError, InvalidParamsError, OperationError, ResponseSystemError
from ..sensor.sensor import Sensor, Sensors
from ..utility import Disable, locked
from .lazy import PagingList
from .requests import config
from .status import Status

if TYPE_CHECKING:
    from .dataset import DatasetClient, FusionDatasetClient

_STRATEGIES = {"abort", "override", "skip"}


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
    _BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

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

    def _calculate_file_sha1(self, local_path: str) -> str:
        sha1_obj = sha1()
        with open(local_path, "rb") as fp:
            while True:
                data = fp.read(self._BUF_SIZE)
                if not data:
                    break
                sha1_obj.update(data)

        return sha1_obj.hexdigest()

    def _post_multipart_formdata(
        self,
        url: str,
        local_path: str,
        remote_path: str,
        data: Dict[str, Any],
    ) -> None:
        with open(local_path, "rb") as fp:
            file_type = filetype.guess_mime(local_path)
            if "x-amz-date" in data:
                data["Content-Type"] = file_type
            data["file"] = (remote_path, fp, file_type)
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
        callback_info: List[Dict[str, Any]],
        skip_uploaded_files: bool = False,
    ) -> None:
        put_data: Dict[str, Any] = {
            "segmentName": self.name,
            "objects": callback_info,
        }
        put_data.update(self._status.get_status_info())

        try:
            self._client.open_api_do("PUT", "multi/callback", self._dataset_id, json=put_data)
        except ResponseSystemError:
            if not skip_uploaded_files:
                raise

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

    @Disable(since="v1.6.0", enabled_in="v1.9.0", reason="TensorBay server refactor")
    def delete_data(self, remote_paths: Union[str, Iterable[str]]) -> None:
        """Delete data of a segment in a certain commit with the given remote paths.

        Arguments:
            remote_paths: The remote paths of data in a segment.

        """
        self._status.check_authority_for_draft()

        all_paths = iter((remote_paths,)) if isinstance(remote_paths, str) else iter(remote_paths)

        while True:
            request_remote_paths = list(islice(all_paths, 128))
            if not request_remote_paths:
                return
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

    def _generate_data(self, offset: int = 0, limit: int = 128) -> Generator[RemoteData, None, int]:
        response = self._list_labels(offset, limit)

        for item in response["labels"]:
            data = RemoteData.loads(item)
            data._url_getter = self._get_url  # pylint: disable=protected-access
            yield data

        return response["totalCount"]  # type: ignore[no-any-return]

    def _upload_or_import_data(self, data: Union[Data, AuthData]) -> Optional[Dict[str, Any]]:
        if isinstance(data, Data):
            callback_info = self._upload_file(data.path, data.target_remote_path)
            if data.label:
                callback_info["label"] = data.label.dumps()
            return callback_info
        self.import_auth_data(data)
        return None

    def _upload_file(self, local_path: str, target_remote_path: str = "") -> Dict[str, Any]:
        """Upload data with local path to the draft.

        Arguments:
            local_path: The local path of the data to upload.
            target_remote_path: The path to save the data in segment client.

        Returns:
            The sha1 and target remote path of the file.

        Raises:
            InvalidParamsError: When target_remote_path does not follow linux style.

        """
        if not target_remote_path:
            target_remote_path = os.path.basename(local_path)

        if "\\" in target_remote_path:
            raise InvalidParamsError(param_name="path", param_value=target_remote_path)

        permission = self._get_upload_permission()
        post_data = permission["result"]

        checksum = self._calculate_file_sha1(local_path)
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
                target_remote_path,
                post_data,
            )

        return {"checksum": checksum, "remotePath": target_remote_path}

    def upload_file(self, local_path: str, target_remote_path: str = "") -> None:
        """Upload data with local path to the draft.

        Arguments:
            local_path: The local path of the data to upload.
            target_remote_path: The path to save the data in segment client.

        """
        self._status.check_authority_for_draft()

        callback_info = self._upload_file(local_path, target_remote_path)

        self._synchronize_upload_info([callback_info])

    def upload_label(self, data: Data) -> None:
        """Upload label with Data object to the draft.

        Arguments:
            data: The data object which represents the local file to upload.

        """
        self._status.check_authority_for_draft()

        self._upload_label(data)

    def upload_data(self, data: Data) -> None:
        """Upload Data object to the draft.

        Arguments:
            data: The :class:`~tensorbay.dataset.data.Data`.

        """
        self._status.check_authority_for_draft()

        callback_info = self._upload_file(data.path, data.target_remote_path)
        if data.label:
            callback_info["label"] = data.label.dumps()
        self._synchronize_upload_info([callback_info])

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

        for start in range(0, len(all_source_remote_paths), 128):
            request_target_remote_paths = all_target_remote_paths[start : start + 128]
            request_source_remote_paths = all_source_remote_paths[start : start + 128]

            if request_target_remote_paths:
                post_data["remotePaths"] = request_target_remote_paths
            post_data["source"]["remotePaths"] = request_source_remote_paths

            self._client.open_api_do("POST", "data?multipleCopy", self._dataset_id, json=post_data)

    def move_data(
        self,
        source_remote_paths: Union[str, Iterable[str]],
        target_remote_paths: Union[None, str, Iterable[str]] = None,
        *,
        source_client: Optional["SegmentClient"] = None,
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

        Raises:
            OperationError: When the type or the length of target_remote_paths is not equal
                with source_remote_paths.
                Or when the dataset_id and drafter_number of source_client
                is not equal with the current segment client.

        """
        self._status.check_authority_for_draft()

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
            "source": source,
            "segmentName": self.name,
        }
        post_data.update(self._status.get_status_info())

        for start in range(0, len(all_source_remote_paths), 128):
            request_target_remote_paths = all_target_remote_paths[start : start + 128]
            request_source_remote_paths = all_source_remote_paths[start : start + 128]

            if request_target_remote_paths:
                post_data["remotePaths"] = request_target_remote_paths
            post_data["source"]["remotePaths"] = request_source_remote_paths

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
        return PagingList(self._generate_data, 128)


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

    def _generate_frames(self, offset: int = 0, limit: int = 128) -> Generator[Frame, None, int]:
        response = self._list_labels(offset, limit)

        for item in response["labels"]:
            frame = Frame.loads(item)
            for data in frame.values():  # pylint: disable=no-member # pylint issue: #3131
                # pylint: disable=protected-access
                data._url_getter = self._get_url  # type: ignore[union-attr]
            yield frame

        return response["totalCount"]  # type: ignore[no-any-return]

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

    def upload_frame(  # pylint: disable=too-many-locals
        self, frame: Frame, timestamp: Optional[float] = None, skip_uploaded_files: bool = False
    ) -> None:
        """Upload frame to the draft.

        Arguments:
            frame: The :class:`~tensorbay.dataset.frame.Frame` to upload.
            timestamp: The mark to sort frames, supporting timestamp and float.
            skip_uploaded_files: Set it to True to skip the uploaded files.

        Raises:
            FrameError: When lacking frame id or frame id conflicts.
            InvalidParamsError: When remote_path does not follow linux style.

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

        for sensor_name, data in frame.items():
            if not isinstance(data, Data):
                continue

            target_remote_path = data.target_remote_path

            if "\\" in target_remote_path:
                raise InvalidParamsError(param_name="path", param_value=target_remote_path)

            permission = self._get_upload_permission()
            post_data = permission["result"]

            checksum = self._calculate_file_sha1(data.path)
            post_data["key"] = permission["extra"]["objectPrefix"] + checksum

            backend_type = permission["extra"]["backendType"]
            if backend_type == "azure":
                url = (
                    f'{permission["extra"]["host"]}{permission["extra"]["objectPrefix"]}'
                    f'{checksum}?{permission["result"]["token"]}'
                )

                self._put_binary_file_to_azure(url, data.path, post_data)
            else:
                self._post_multipart_formdata(
                    permission["extra"]["host"],
                    data.path,
                    target_remote_path,
                    post_data,
                )

            frame_info: Dict[str, Any] = {
                "sensorName": sensor_name,
                "frameId": str(frame_id),
            }
            if hasattr(data, "timestamp"):
                frame_info["timestamp"] = data.timestamp

            callback_info = {
                "checksum": checksum,
                "remotePath": target_remote_path,
                "label": data.label.dumps(),
            }
            callback_info.update(frame_info)
            self._synchronize_upload_info([callback_info], skip_uploaded_files)

    def list_frames(self) -> PagingList[Frame]:
        """List required frames in the segment in a certain commit.

        Returns:
            The PagingList of :class:`~tensorbay.dataset.frame.Frame`.

        """
        return PagingList(self._generate_frames, 128)
