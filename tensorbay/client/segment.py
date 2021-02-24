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
In contrast to the :class:`SegmentClient`, :class:`Segment` is a local concept.
It represents a segment created locally. Please refer to :class:`Segment` for more information.

Similarly to the :class:`SegmentClient`, the :class:`FusionSegmentClient` represents
the fusion segment in a fusion dataset on TensorBay, and its local counterpart
is :class:`FusionSegment`. Please refer to :class:`FusionSegment`
for more information.

Todo:
    Add `../dataset/segment.py` link.
    Add `../dataset/frame.py` link.

"""

import os
import sys
import threading
import time
import uuid
from copy import deepcopy
from pathlib import PurePosixPath
from typing import Any, Dict, Iterator, Optional, Tuple

import filetype
from requests_toolbelt import MultipartEncoder

from ..dataset import Data, Frame
from ..sensor.sensor import Sensor, _SensorType
from ..utility import TBRN, TBRNType
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
        commit_id: Dataset commit ID.

    """

    _PERMISSION_CATEGORY: str
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

    @property
    def name(self) -> str:
        """Get the name of this segment client.

        Returns:
            The name of the segment.

        """
        return self._name

    @property
    def dataset_id(self) -> str:
        """Get the dataset ID.

        Returns:
            The dataset ID.

        """
        return self._dataset_id

    @property
    def commit_id(self) -> Optional[str]:
        """Get the dataset commit ID.

        Returns:
            The dataset commit ID.

        """
        return self._commit_id

    def _get_url(self, tbrn: TBRN) -> str:
        """Get url of a specific remote path.

        Arguments:
            tbrn: TensorBay Resource Name.

        Returns:
            The url of the input remote_path and sensor_name.

        """
        params = {
            "segmentName": self._name,
            "remotePath": tbrn.remote_path,
        }
        if tbrn.type == TBRNType.FUSION_FILE:
            params["sensorName"] = tbrn.sensor_name
        response = self._client.open_api_do("GET", "data/urls", self.dataset_id, params=params)
        return response.json()["url"]  # type: ignore[no-any-return]

    def _list_labels(
        self, *, start: int = 0, stop: int = sys.maxsize, page_size: int = 128
    ) -> Iterator[Dict[str, Any]]:
        """List labels in a segment client.

        Arguments:
            start: The index of label to start.
            stop: The index of label to stop.
            page_size: The page size for the listed labels.

        Yields:
            Labels in a segment client.

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

    def _upload_label(self, data: Data, sensor_name: Optional[str] = None) -> None:
        post_data: Dict[str, Any] = {
            "segmentName": self.name,
            "remotePath": data.remote_path,
            "labelValues": data.labels.dumps(),
        }
        if sensor_name:
            post_data["sensorName"] = sensor_name
        self._client.open_api_do("PUT", "labels", self.dataset_id, json=post_data)


class SegmentClient(SegmentClientBase):
    """This class defines :class:`SegmentClient`.

    :class:`SegmentClient` inherits from SegmentClientBase and provides methods within a
    segment scope, such as `upload_label()`, `upload_data()`, `list_data()` and so on.
    In contrast to FusionSegmentClient, :class:`SegmentClient` has only one sensor.

    """

    def upload_data(self, local_path: str, remote_path: str = "") -> None:
        """Upload data with local path to the segment.

        Arguments:
            local_path: The local path of the data to upload.
            remote_path: The path to save the data in segment client.

        Raises:
            GASPathError: If remote_path does not follow linux style.
            GASException: If uploading data failed.

        """
        if not remote_path:
            remote_path = os.path.basename(local_path)

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
                local_path,
                remote_path,
                post_data,
            )

            self._synchronize_upload_info(post_data["key"], version_id, etag)

        except GASException:
            self._clear_upload_permission()
            raise

    def upload_label(self, data: Data) -> None:
        """Upload label with Data object to the segment.

        Arguments:
            data: The data object which represents the local file to upload.

        """
        self._upload_label(data)

    def upload_data_object(self, data: Data) -> None:
        """Upload data with Data object to the segment.

        Arguments:
            data: The data object which represents the local file to upload.

        """
        self.upload_data(data.local_path, data.remote_path)
        self._upload_label(data)

    def _list_data(
        self, *, start: int = 0, stop: int = sys.maxsize, page_size: int = 128
    ) -> Iterator[Dict[str, Any]]:
        """List data in a segment client.

        Arguments:
            start: The index of data to start.
            stop: The index of data to stop.
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

    def list_data(self, *, start: int = 0, stop: int = sys.maxsize) -> Iterator[str]:
        """List required data path in a segment client.

        Arguments:
            start: The index to start.
            stop: The index to end.

        Yields:
            Required data paths in a segment client.

        """
        yield from (item["remotePath"] for item in self._list_data(start=start, stop=stop))

    def list_data_objects(self, *, start: int = 0, stop: int = sys.maxsize) -> Iterator[Data]:
        """List required Data object in a dataset segment.

        Arguments:
            start: The index to start.
            stop: The index to stop.

        Yields:
            Required Data object.

        """
        for labels in self._list_labels(start=start, stop=stop):
            remote_path = labels["remotePath"]
            tbrn = TBRN(self._dataset_name, self._name, remote_path=remote_path)
            data = Data(tbrn, url_getter=self._get_url)
            data.labels._loads(labels["label"])  # pylint: disable=protected-access
            yield data


class FusionSegmentClient(SegmentClientBase):
    """This class defines :class:`FusionSegmentClient`.

    :class:`FusionSegmentClient` inherits from :class:`SegmentClientBase` and provides
    methods within a fusion segment scope, such as :meth:`FusionSegment.upload_sensor_object`,
    :meth:`FusionSegment.upload_frame_object` and :meth:`FusionSegment.list_frame_objects`.

    In contrast to :class:`SegmentClient`, :class:`FusionSegmentClient` has multiple sensors.

    """

    def list_sensor_objects(self) -> Iterator[_SensorType]:
        """List required sensor object in a segment client.

        Yields:
            Required sensor objects in a segment client.

        """
        params: Dict[str, Any] = {"segmentName": self._name}
        if self._commit_id:
            params["commit"] = self._commit_id

        response = self._client.open_api_do("GET", "sensors", self.dataset_id, params=params).json()

        for sensor_info in response["sensors"]:
            yield Sensor.loads(sensor_info)  # type: ignore[misc]

    def upload_sensor_object(self, sensor: Sensor) -> None:
        """Upload sensor to the :class:`SegmentClient`.

        Arguments:
            sensor: The sensor to upload.

        """
        post_data = sensor.dumps()

        post_data["segmentName"] = self._name
        self._client.open_api_do("POST", "sensors", self.dataset_id, json=post_data)

    def delete_sensor(self, sensor_name: str) -> None:
        """Delete a TensorBay sensor with the given sensor name.

        Arguments:
            sensor_name: The TensorBay sensor to delete.

        """
        delete_data: Dict[str, str] = {"segmentName": self._name, "sensorName": sensor_name}

        self._client.open_api_do("DELETE", "sensors", self.dataset_id, json=delete_data)

    def upload_frame_object(self, frame: Frame, frame_index: Optional[int] = None) -> None:
        """Upload :class:`Frame` to the :class:`SegmentClient`.

        Arguments:
            frame: The :class:`Frame` to upload.
            frame_index: The frame index, used for TensorBay to sort the frame.

        Raises:
            GASPathError: If remote_path does not follow linux style.
            TypeError: If frame has no frame index or has no timestamp.
            GASException: If uploading frame failed.

        """
        frame_id = str(uuid.uuid4())

        for sensor_name, data in frame.items():
            remote_path = data.remote_path

            if "\\" in remote_path:
                raise GASPathError(remote_path)

            if frame_index is None and not hasattr(data, "timestamp"):
                raise TypeError(
                    "Either 'frame_index' or 'timestamp' is necessary for sorting frames"
                )

            permission = self._get_upload_permission()
            post_data = permission["result"]

            path = str(PurePosixPath(sensor_name, remote_path))
            post_data["key"] = permission["extra"]["objectPrefix"] + path

            del post_data["x:category"]
            del post_data["x:id"]

            try:
                version_id, etag = self._post_multipart_formdata(
                    permission["extra"]["host"],
                    data.local_path,
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
                if frame_index is not None:
                    frame_info["frameIndex"] = frame_index

                self._synchronize_upload_info(post_data["key"], version_id, etag, frame_info)

            except GASException:
                self._clear_upload_permission()
                raise
            self._upload_label(data, sensor_name)

    def _list_frames(
        self, *, start: int = 0, stop: int = sys.maxsize, page_size: int = 128
    ) -> Iterator[Dict[str, Any]]:
        """List all frames in a segment client(Fusion dataset).

        Arguments:
            start: The index of frame to start.
            stop: The index of frame to stop.
            page_size: The page size for listed frames.

        Yields:
             All fusion data.

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

    def list_frame_objects(self, *, start: int = 0, stop: int = sys.maxsize) -> Iterator[Frame]:
        """List required frames in the segment.

        Arguments:
            start: The index of frame to start.
            stop: The index of frame to stop.

        Yields:
            Required :class:`Frame`.

        """
        for labels in self._list_labels(start=start, stop=stop):
            frame_index = labels["frameIndex"]
            frame_id = labels["frameId"]
            frame = Frame(frame_index, frame_id)
            for data_info in labels["frame"]:
                sensor_name = data_info["sensorName"]
                remote_path = data_info["remotePath"]
                tbrn = TBRN(
                    self._dataset_name,
                    self._name,
                    frame_index,
                    sensor_name,
                    remote_path=remote_path,
                )
                data = Data(tbrn, timestamp=data_info["timestamp"], url_getter=self._get_url)
                data.labels._loads(data_info["label"])  # pylint: disable=protected-access
                frame[sensor_name] = data
            yield frame
