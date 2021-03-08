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
import sys
import threading
import time
from copy import deepcopy
from itertools import islice
from typing import Any, Dict, Iterable, Iterator, Optional, Tuple, Union

import filetype
import ulid
from requests_toolbelt import MultipartEncoder

from ..dataset import Data, Frame, RemoteData
from ..sensor.sensor import Sensor
from .exceptions import GASException, GASPathError
from .requests import Client, default_config, paging_range

_SERVER_VERSION_MATCH: Dict[str, str] = {
    "AmazonS3": "x-amz-version-id",
    "AliyunOSS": "x-oss-version-id",
}


class SegmentClientBase:
    """This class defines the basic concept of :class:`SegmentClient`.

    A :class:`SegmentClientBase` contains the information needed for determining
        a unique segment in a dataset on TensorBay.

    Arguments:
        name: Segment name.
        dataset_id: Dataset ID.
        dataset_name: Dataset name.
        client: The client used for sending request to TensorBay.
        commit_id: The commit ID.

    """

    _EXPIRED_IN_SECOND = 240

    def __init__(  # pylint: disable=too-many-arguments
        self,
        name: str,
        dataset_id: str,
        dataset_name: str,
        client: Client,
        commit_id: Optional[str] = None,
    ) -> None:
        self._name = name
        self._dataset_id = dataset_id
        self._dataset_name = dataset_name
        self._client = client
        self._commit_id = commit_id
        self._permission: Dict[str, Any] = {"expireAt": 0}
        self._permission_lock = threading.Lock()

    def _get_url(self, remote_path: str) -> str:
        """Get URL of a specific remote path.

        Arguments:
            remote_path: The remote path of the file.

        Returns:
            The URL of the remote file.

        """
        params = {
            "segmentName": self._name,
            "remotePath": remote_path,
        }
        response = self._client.open_api_do("GET", "data/urls", self.dataset_id, params=params)
        return response.json()["url"]  # type: ignore[no-any-return]

    def _list_labels(
        self, *, start: int = 0, stop: int = sys.maxsize, page_size: int = 128
    ) -> Iterator[Dict[str, Any]]:
        """List labels of the segment in a certain commit.

        Arguments:
            start: The index to start.
            stop: The index to stop.
            page_size: The page size for the listed labels.

        Yields:
            Labels in a segment in a certain commit.

        """
        params: Dict[str, Any] = {"segmentName": self._name}
        if self._commit_id:
            params["commit"] = self._commit_id

        for params["offset"], params["limit"] in paging_range(start, stop, page_size):
            response = self._client.open_api_do(
                "GET", "labels", self.dataset_id, params=params
            ).json()
            yield from response["labels"]
            if response["recordSize"] + response["offset"] >= response["totalCount"]:
                break

    def _get_upload_permission(self) -> Dict[str, Any]:
        with self._permission_lock:
            if int(time.time()) >= self._permission["expireAt"]:
                params = {
                    "expired": self._EXPIRED_IN_SECOND,
                    "segmentName": self._name,
                }
                self._permission = self._client.open_api_do(
                    "GET", "policies", self.dataset_id, params=params
                ).json()

                if default_config.is_intern:
                    urlsplit = self._permission["extra"]["host"].rsplit(".", 2)
                    urlsplit[0] += "-internal"
                    self._permission["extra"]["host"] = ".".join(urlsplit)

            return deepcopy(self._permission)

    def _clear_upload_permission(self) -> None:
        with self._permission_lock:
            self._permission = {"expireAt": 0}

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

    def _synchronize_upload_info(
        self, key: str, version_id: str, etag: str, frame_info: Optional[Dict[str, Any]] = None
    ) -> None:
        put_data = {
            "key": key,
            "versionId": version_id,
            "etag": etag,
        }
        if frame_info:
            put_data.update(frame_info)

        self._client.open_api_do("PUT", "callback", self.dataset_id, json=put_data)

    def _upload_label(self, data: Data) -> None:
        post_data: Dict[str, Any] = {
            "segmentName": self.name,
            "remotePath": data.target_remote_path,
            "labelValues": data.label.dumps(),
        }
        self._client.open_api_do("PUT", "labels", self.dataset_id, json=post_data)

    @property
    def name(self) -> str:
        """Return the segment name.

        Returns:
            The segment name.

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
    def commit_id(self) -> Optional[str]:
        """Return the commit ID.

        Returns:
            The commit ID.

        """
        return self._commit_id

    def delete_data(self, remote_paths: Union[str, Iterable[str]]) -> None:
        """Delete data of a segment in a certain commit with the given remote paths.

        Arguments:
            remote_paths: The remote paths of data in a segment.

        """
        all_paths = iter((remote_paths,)) if isinstance(remote_paths, str) else iter(remote_paths)

        while True:
            request_remote_paths = list(islice(all_paths, 128))
            if not request_remote_paths:
                return
            delete_data: Dict[str, Any] = {
                "segmentName": self.name,
                "remotePaths": request_remote_paths,
            }
            self._client.open_api_do("DELETE", "data", self.dataset_id, json=delete_data)


class SegmentClient(SegmentClientBase):
    """This class defines :class:`SegmentClient`.

    :class:`SegmentClient` inherits from SegmentClientBase and provides methods within a
    segment scope, such as `upload_label()`, `upload_data()`, `list_data()` and so on.
    In contrast to FusionSegmentClient, :class:`SegmentClient` has only one sensor.

    """

    def _list_data(
        self, *, start: int = 0, stop: int = sys.maxsize, page_size: int = 128
    ) -> Iterator[Dict[str, Any]]:
        """List data in a segment in a certain commit.

        Arguments:
            start: The index to start.
            stop: The index to stop.
            page_size: The page size for listed data.

        Yields:
            Data in a segment client.

        """
        params: Dict[str, Any] = {"segmentName": self._name}
        if self._commit_id:
            params["commit"] = self._commit_id

        for params["offset"], params["limit"] in paging_range(start, stop, page_size):
            response = self._client.open_api_do(
                "GET", "data", self.dataset_id, params=params
            ).json()
            yield from response["data"]
            if response["recordSize"] + response["offset"] >= response["totalCount"]:
                break

    def upload_file(self, local_path: str, target_remote_path: str = "") -> None:
        """Upload data with local path to the draft.

        Arguments:
            local_path: The local path of the data to upload.
            target_remote_path: The path to save the data in segment client.

        Raises:
            GASPathError: When target_remote_path does not follow linux style.
            GASException: When uploading data failed.

        """
        if not target_remote_path:
            target_remote_path = os.path.basename(local_path)

        if "\\" in target_remote_path:
            raise GASPathError(target_remote_path)

        permission = self._get_upload_permission()
        post_data = permission["result"]
        post_data["key"] = permission["extra"]["objectPrefix"] + target_remote_path

        del post_data["x:category"]
        del post_data["x:id"]
        try:
            version_id, etag = self._post_multipart_formdata(
                permission["extra"]["host"],
                local_path,
                target_remote_path,
                post_data,
            )

            self._synchronize_upload_info(post_data["key"], version_id, etag)

        except GASException:
            self._clear_upload_permission()
            raise

    def upload_label(self, data: Data) -> None:
        """Upload label with Data object to the draft.

        Arguments:
            data: The data object which represents the local file to upload.

        """
        self._upload_label(data)

    def upload_data(self, data: Data) -> None:
        """Upload Data object to the draft.

        Arguments:
            data: The :class:`~tensorbay.dataset.data.Data`.

        """
        self.upload_file(data.path, data.target_remote_path)
        self._upload_label(data)

    def list_data_paths(self, *, start: int = 0, stop: int = sys.maxsize) -> Iterator[str]:
        """List required data path in a segment in a certain commit.

        Arguments:
            start: The index to start.
            stop: The index to end.

        Yields:
            Required data paths.

        """
        yield from (item["remotePath"] for item in self._list_data(start=start, stop=stop))

    def list_data(self, *, start: int = 0, stop: int = sys.maxsize) -> Iterator[RemoteData]:
        """List required Data object in a dataset segment.

        Arguments:
            start: The index to start.
            stop: The index to stop.

        Yields:
            Required Data object.

        """
        for data_content in self._list_labels(start=start, stop=stop):
            data = RemoteData.loads(data_content)
            data._url_getter = self._get_url  # pylint: disable=protected-access
            yield data


class FusionSegmentClient(SegmentClientBase):
    """This class defines :class:`FusionSegmentClient`.

    :class:`FusionSegmentClient` inherits from :class:`SegmentClientBase` and provides
    methods within a fusion segment scope, such as
    :meth:`FusionSegmentClient.upload_sensor`,
    :meth:`FusionSegmentClient.upload_frame`
    and :meth:`FusionSegmentClient.list_frames`.

    In contrast to :class:`SegmentClient`, :class:`FusionSegmentClient` has multiple sensors.

    """

    def _list_frames(
        self, *, start: int = 0, stop: int = sys.maxsize, page_size: int = 128
    ) -> Iterator[Dict[str, Any]]:
        """List all frames in a segment in a certain commit.

        Arguments:
            start: The index to start.
            stop: The index to stop.
            page_size: The page size for listed frames.

        Yields:
             Required frames.

        """
        params: Dict[str, Any] = {"segmentName": self._name}
        if self._commit_id:
            params["commit"] = self._commit_id

        for params["offset"], params["limit"] in paging_range(start, stop, page_size):
            response = self._client.open_api_do(
                "GET", "data", self.dataset_id, params=params
            ).json()
            yield from response["data"]
            if response["recordSize"] + response["offset"] >= response["totalCount"]:
                break

    def list_sensors(self) -> Iterator["Sensor._Type"]:
        """List required sensor object in a segment client.

        Yields:
            Required sensor objects.

        """
        params: Dict[str, Any] = {"segmentName": self._name}
        if self._commit_id:
            params["commit"] = self._commit_id

        response = self._client.open_api_do("GET", "sensors", self.dataset_id, params=params).json()

        for sensor_info in response["sensors"]:
            yield Sensor.loads(sensor_info)

    def upload_sensor(self, sensor: Sensor) -> None:
        """Upload sensor to the draft.

        Arguments:
            sensor: The sensor to upload.

        """
        post_data = sensor.dumps()

        post_data["segmentName"] = self._name
        self._client.open_api_do("POST", "sensors", self.dataset_id, json=post_data)

    def delete_sensor(self, sensor_name: str) -> None:
        """Delete a TensorBay sensor of the draft with the given sensor name.

        Arguments:
            sensor_name: The TensorBay sensor to delete.

        """
        delete_data: Dict[str, str] = {"segmentName": self._name, "sensorName": sensor_name}

        self._client.open_api_do("DELETE", "sensors", self.dataset_id, json=delete_data)

    def upload_frame(self, frame: Frame, timestamp: Optional[float] = None) -> None:
        """Upload frame to the draft.

        Arguments:
            frame: The :class:`~tensorbay.dataset.frame.Frame` to upload.
            timestamp: The mark to sort frames, supporting timestamp and float.

        Raises:
            GASPathError: When remote_path does not follow linux style.
            GASException: When uploading frame failed.
            TypeError: When frame id conflicts。                                `

        """
        if timestamp is None:
            try:
                frame_id = frame.frame_id
            except AttributeError as error:
                raise TypeError(
                    "Lack frame id, please add frame id in frame or "
                    "give timestamp to the function!"
                ) from error
        elif hasattr(frame, "frame_id"):
            raise TypeError("Frame id conflicts, please do not give timestamp to the function!.")
        else:
            frame_id = str(ulid.from_timestamp(timestamp))

        for sensor_name, data in frame.items():
            if not isinstance(data, Data):
                continue

            remote_path = data.target_remote_path

            if "\\" in remote_path:
                raise GASPathError(remote_path)

            permission = self._get_upload_permission()
            post_data = permission["result"]
            post_data["key"] = permission["extra"]["objectPrefix"] + remote_path

            del post_data["x:category"]
            del post_data["x:id"]

            try:
                version_id, etag = self._post_multipart_formdata(
                    permission["extra"]["host"],
                    data.path,
                    remote_path,
                    post_data,
                )

                frame_info: Dict[str, Any] = {
                    "segmentName": self._name,
                    "sensorName": sensor_name,
                    "frameId": frame_id,
                }
                if hasattr(data, "timestamp"):
                    frame_info["timestamp"] = data.timestamp

                self._synchronize_upload_info(post_data["key"], version_id, etag, frame_info)

            except GASException:
                self._clear_upload_permission()
                raise
            self._upload_label(data)

    def list_frames(self, *, start: int = 0, stop: int = sys.maxsize) -> Iterator[Frame]:
        """List required frames in the segment in a certain commit.

        Arguments:
            start: The index to start.
            stop: The index to stop.

        Yields:
            Required :class:`~tensorbay.dataset.frame.Frame`.

        """
        for frame_content in self._list_labels(start=start, stop=stop):
            frame = Frame.loads(frame_content)
            for data in frame.values():  # pylint: disable=no-member # pylint issue: #3131
                # pylint: disable=protected-access
                data._url_getter = self._get_url  # type: ignore[union-attr]
            yield frame
