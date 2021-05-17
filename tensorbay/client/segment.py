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
from itertools import islice
from typing import TYPE_CHECKING, Any, Dict, Generator, Iterable, Optional, Tuple, Union

import filetype
from requests_toolbelt import MultipartEncoder
from ulid import from_timestamp

from ..dataset import Data, Frame, RemoteData
from ..exception import FrameError, InvalidParamsError, ResponseSystemError
from ..sensor.sensor import Sensor, Sensors
from ..utility import locked
from .commit_status import CommitStatus
from .requests import PagingList, config

if TYPE_CHECKING:
    from .dataset import DatasetClient, FusionDatasetClient


_SERVER_VERSION_MATCH: Dict[str, str] = {
    "AmazonS3": "x-amz-version-id",
    "AliyunOSS": "x-oss-version-id",
}


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

    def _get_upload_permission(self) -> Dict[str, Any]:
        if int(time.time()) >= self._permission["expireAt"]:
            self._request_upload_permission()

        return deepcopy(self._permission)

    def _post_multipart_formdata(
        self,
        url: str,
        local_path: str,
        remote_path: str,
        data: Dict[str, Any],
    ) -> Tuple[str, str]:
        with open(local_path, "rb") as fp:
            file_type = filetype.guess_mime(local_path)
            if "x-amz-date" in data:
                data["Content-Type"] = file_type
            data["file"] = (remote_path, fp, file_type)
            multipart = MultipartEncoder(data)
            response_headers = self._client.do(
                "POST", url, data=multipart, headers={"Content-Type": multipart.content_type}
            ).headers
            version = _SERVER_VERSION_MATCH[response_headers["Server"]]
            return response_headers[version], response_headers["ETag"].strip('"')

    def _put_binary_file_to_azure(
        self,
        url: str,
        local_path: str,
        data: Dict[str, Any],
    ) -> Tuple[str, str]:
        with open(local_path, "rb") as fp:
            file_type = filetype.guess_mime(local_path)
            request_headers = {
                "x-ms-blob-content-type": file_type,
                "x-ms-blob-type": data["x-ms-blob-type"],
            }
            response_headers = self._client.do("PUT", url, data=fp, headers=request_headers).headers
            return response_headers["x-ms-version-id"], response_headers["ETag"].strip('"')

    def _synchronize_upload_info(  # pylint: disable=too-many-arguments
        self,
        key: str,
        version_id: str,
        etag: str,
        frame_info: Optional[Dict[str, Any]] = None,
        skip_uploaded_files: bool = False,
    ) -> None:
        put_data: Dict[str, Any] = {
            "key": key,
            "versionId": version_id,
            "etag": etag,
        }
        put_data.update(self._status.get_status_info())

        if frame_info:
            put_data.update(frame_info)

        try:
            self._client.open_api_do("PUT", "callback", self._dataset_id, json=put_data)
        except ResponseSystemError:
            if not skip_uploaded_files:
                raise

    def _upload_label(self, data: Data) -> None:
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
    def status(self) -> CommitStatus:
        """Return the status of the dataset client.

        Returns:
            The status of the dataset client.

        """
        return self._status

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

    def upload_file(self, local_path: str, target_remote_path: str = "") -> None:
        """Upload data with local path to the draft.

        Arguments:
            local_path: The local path of the data to upload.
            target_remote_path: The path to save the data in segment client.

        Raises:
            InvalidParamsError: When target_remote_path does not follow linux style.

        """
        self._status.check_authority_for_draft()

        if not target_remote_path:
            target_remote_path = os.path.basename(local_path)

        if "\\" in target_remote_path:
            raise InvalidParamsError(param_name="path", param_value=target_remote_path)

        permission = self._get_upload_permission()
        post_data = permission["result"]
        post_data["key"] = permission["extra"]["objectPrefix"] + target_remote_path

        backend_type = permission["extra"]["backendType"]
        if backend_type == "azure":
            url = (
                f'{permission["extra"]["host"]}{permission["extra"]["objectPrefix"]}'
                f'{target_remote_path}?{permission["result"]["token"]}'
            )

            version_id, etag = self._put_binary_file_to_azure(url, local_path, post_data)
        else:
            version_id, etag = self._post_multipart_formdata(
                permission["extra"]["host"],
                local_path,
                target_remote_path,
                post_data,
            )

        self._synchronize_upload_info(post_data["key"], version_id, etag)

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

        self.upload_file(data.path, data.target_remote_path)
        self._upload_label(data)

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
            post_data["key"] = permission["extra"]["objectPrefix"] + target_remote_path

            backend_type = permission["extra"]["backendType"]
            if backend_type == "azure":
                url = (
                    f'{permission["extra"]["host"]}{permission["extra"]["objectPrefix"]}'
                    f'{target_remote_path}?{permission["result"]["token"]}'
                )

                version_id, etag = self._put_binary_file_to_azure(url, data.path, post_data)
            else:
                version_id, etag = self._post_multipart_formdata(
                    permission["extra"]["host"],
                    data.path,
                    target_remote_path,
                    post_data,
                )

            frame_info: Dict[str, Any] = {
                "segmentName": self._name,
                "sensorName": sensor_name,
                "frameId": str(frame_id),
            }
            if hasattr(data, "timestamp"):
                frame_info["timestamp"] = data.timestamp

            self._synchronize_upload_info(
                post_data["key"], version_id, etag, frame_info, skip_uploaded_files
            )

            self._upload_label(data)

    def list_frames(self) -> PagingList[Frame]:
        """List required frames in the segment in a certain commit.

        Returns:
            The PagingList of :class:`~tensorbay.dataset.frame.Frame`.

        """
        return PagingList(self._generate_frames, 128)
