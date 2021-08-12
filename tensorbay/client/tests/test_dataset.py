#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest
from ulid import ULID, from_timestamp

from ...dataset import Data, Frame, FusionSegment, Notes, RemoteData, Segment
from ...exception import (
    InvalidParamsError,
    NameConflictError,
    OperationError,
    ResourceNotExistError,
)
from ...label import Catalog
from .. import dataset, gas, segment
from ..dataset import DatasetClient, FusionDatasetClient
from ..diff import DataDiff, SegmentDiff
from ..gas import DEFAULT_BRANCH, GAS
from ..lazy import ReturnGenerator
from ..requests import Tqdm
from ..segment import FusionSegmentClient, SegmentClient
from ..status import Status
from ..struct import ROOT_COMMIT_ID
from .utility import mock_response


class TestDatasetClientBase:
    gas_client = GAS("Accesskey-********************************")
    dataset_client = DatasetClient(
        "test_dataset",
        "12345",
        gas_client,
        status=Status(DEFAULT_BRANCH, commit_id=ROOT_COMMIT_ID),
    )
    source_dataset_client = DatasetClient(
        "source_dataset",
        "544321",
        gas_client,
        status=Status(DEFAULT_BRANCH, commit_id=ROOT_COMMIT_ID),
    )

    def test__create_segment(self, mocker):
        post_data = {"name": "train"}
        post_data.update(self.dataset_client._status.get_status_info())
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(),
        )
        self.dataset_client._create_segment("train")
        open_api_do.assert_called_once_with(
            "POST", "segments", self.dataset_client.dataset_id, json=post_data
        )

    def test__list_segment(self, mocker):
        params = self.dataset_client._status.get_status_info()
        offset, limit = 0, 128
        params["offset"] = offset
        params["limit"] = limit
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(),
        )
        self.dataset_client._list_segments()
        open_api_do.assert_called_once_with(
            "GET", "segments", self.dataset_client._dataset_id, params=params
        )

    def test__generate_segment_names(self, mocker):
        params = self.dataset_client._status.get_status_info()
        offset, limit = 0, 128
        params["offset"] = offset
        params["limit"] = limit
        response_data = {
            "offset": 0,
            "recordSize": 2,
            "totalCount": 2,
            "segments": [
                {"name": "test", "description": ""},
                {"name": "train", "description": ""},
            ],
        }
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=response_data),
        )
        assert list(self.dataset_client._generate_segment_names()) == [
            segment["name"] for segment in response_data["segments"]
        ]
        open_api_do.assert_called_once_with(
            "GET", "segments", self.dataset_client._dataset_id, params=params
        )

    def test__copy_segment(self, mocker):
        self.dataset_client._status.checkout(draft_number=1)
        source_name, target_name = "default", "train"
        with pytest.raises(InvalidParamsError):
            self.dataset_client._copy_segment(
                source_name, target_name, source_client=None, strategy="move"
            )

        with pytest.raises(OperationError):
            self.dataset_client._copy_segment(source_name, source_name, source_client=None)

        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(),
        )

        source = {"segmentName": source_name}
        source["id"] = self.source_dataset_client.dataset_id
        source.update(self.source_dataset_client.status.get_status_info())
        post_data = {
            "strategy": "abort",
            "source": source,
            "segmentName": target_name,
        }
        post_data.update(self.dataset_client._status.get_status_info())
        self.dataset_client._copy_segment(
            source_name, target_name, source_client=self.source_dataset_client
        )
        open_api_do.assert_called_once_with(
            "POST", "segments?copy", self.dataset_client._dataset_id, json=post_data
        )

    def test__move_segment(self, mocker):
        self.dataset_client._status.checkout(draft_number=1)
        source_name, target_name = "default", "train"
        with pytest.raises(InvalidParamsError):
            self.dataset_client._move_segment(source_name, target_name, strategy="move")

        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(),
        )
        post_data = {
            "strategy": "abort",
            "source": {"segmentName": source_name},
            "segmentName": target_name,
        }
        post_data.update(self.dataset_client._status.get_status_info())
        self.dataset_client._move_segment(source_name, target_name)
        open_api_do.assert_called_once_with(
            "POST", "segments?move", self.dataset_client._dataset_id, json=post_data
        )

    def test_update_notes(self, mocker):
        self.dataset_client._status.checkout(draft_number=1)

        patch_data = {"binPointCloudFields": None}
        patch_data.update(self.dataset_client._status.get_status_info())

        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(),
        )
        self.dataset_client.update_notes(bin_point_cloud_fields=None)
        open_api_do.assert_called_once_with(
            "PATCH", "notes", self.dataset_client._dataset_id, json=patch_data
        )

        patch_data = {
            "isContinuous": True,
            "binPointCloudFields": ["X", "Y", "Z", "Intensity", "Ring"],
        }
        patch_data.update(self.dataset_client._status.get_status_info())
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(),
        )
        self.dataset_client.update_notes(
            is_continuous=True, bin_point_cloud_fields=["X", "Y", "Z", "Intensity", "Ring"]
        )
        open_api_do.assert_called_once_with(
            "PATCH", "notes", self.dataset_client._dataset_id, json=patch_data
        )

    def test_get_notes(self, mocker):
        params = self.dataset_client._status.get_status_info()
        response_data = {
            "isContinuous": True,
            "binPointCloudFields": ["X", "Y", "Z", "Intensity", "Ring"],
        }
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=response_data),
        )
        assert self.dataset_client.get_notes() == Notes.loads(response_data)
        open_api_do.assert_called_once_with(
            "GET", "notes", self.dataset_client._dataset_id, params=params
        )

    def test_list_segment(self, mocker):
        response_data = {
            "offset": 0,
            "recordSize": 2,
            "totalCount": 2,
            "segments": [
                {"name": "test", "description": ""},
                {"name": "train", "description": ""},
            ],
        }
        mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=response_data),
        )
        assert list(self.dataset_client.list_segment_names()) == [
            segment["name"] for segment in response_data["segments"]
        ]

    def test_get_catelog(self, mocker):
        params = self.dataset_client._status.get_status_info()
        response_data = {"catalog": {"CLASSIFICATION": {"categories": [{"name": "cat"}]}}}
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=response_data),
        )
        assert self.dataset_client.get_catalog() == Catalog.loads(response_data["catalog"])
        open_api_do.assert_called_once_with(
            "GET", "labels/catalogs", self.dataset_client._dataset_id, params=params
        )

    def test_upload_catalog(self, mocker):
        self.dataset_client._status.checkout(draft_number=1)
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(),
        )
        catalog = Catalog.loads({"CLASSIFICATION": {"categories": [{"name": "cat"}]}})
        self.dataset_client.upload_catalog(catalog)
        put_data = {"catalog": catalog.dumps()}
        put_data.update(self.dataset_client._status.get_status_info())
        open_api_do.assert_called_once_with(
            "PUT", "labels/catalogs", self.dataset_client._dataset_id, json=put_data
        )

    def test_delete_segment(self, mocker):
        self.dataset_client._status.checkout(draft_number=1)
        delete_data = {"segmentName": "train"}
        delete_data.update(self.dataset_client._status.get_status_info())
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(),
        )
        self.dataset_client.delete_segment("train")
        open_api_do.assert_called_once_with(
            "DELETE", "segments", self.dataset_client._dataset_id, json=delete_data
        )


class TestDatasetClient(TestDatasetClientBase):
    def test__generate_segments(self, mocker):
        params = self.dataset_client._status.get_status_info()
        offset, limit = 0, 128
        params["offset"] = offset
        params["limit"] = limit
        response_data = {
            "offset": 0,
            "recordSize": 2,
            "totalCount": 2,
            "segments": [
                {"name": "test", "description": ""},
                {"name": "train", "description": ""},
            ],
        }
        list_segments = mocker.patch(
            f"{dataset.__name__}.DatasetClient._list_segments",
            return_value=response_data,
        )
        segment_generator = ReturnGenerator(self.dataset_client._generate_segments())
        assert [segment.name for segment in segment_generator] == [
            item["name"] for item in response_data["segments"]
        ]
        list_segments.assert_called_once_with(offset, limit)
        assert segment_generator.value == response_data["totalCount"]

    def test__generate_segment_diffs(self, mocker):
        params = {"offset": 0, "limit": 128}
        basehead = "commit-fc2cf9f910b7446aaccc7b833fe4e178"
        segment_diffs = {
            "segments": [
                {
                    "name": "test_segment",
                    "action": "modify",
                    "data": {
                        "stats": {"total": 2, "additions": 2, "deletions": 0, "modifications": 0}
                    },
                    "sensor": {"action": ""},
                }
            ],
            "totalCount": 1,
        }
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=segment_diffs),
        )
        data_diffs = [
            DataDiff.loads(
                {
                    "remotePath": "1629800110640323954/3.png",
                    "action": "add",
                    "file": {"action": "add"},
                    "label": {"action": ""},
                }
            ),
            DataDiff.loads(
                {
                    "remotePath": "1629800110640323954/4.png",
                    "action": "add",
                    "file": {"action": "add"},
                    "label": {"action": ""},
                }
            ),
        ]
        list_data_diffs = mocker.patch(
            f"{dataset.__name__}.DatasetClient._list_data_diffs",
            return_value=data_diffs,
        )
        segment_diff_generator = ReturnGenerator(
            self.dataset_client._generate_segment_diffs(basehead)
        )
        for segment_diff_instance, segment_diff in zip(
            segment_diff_generator, segment_diffs["segments"]
        ):
            assert len(segment_diff_instance) == segment_diff["data"]["stats"]["total"]
            assert segment_diff_instance.action == segment_diff["action"]
            assert segment_diff_instance.name == "test_segment"
            for data_diff_instance, data_diff in zip(segment_diff_instance, data_diffs):
                assert data_diff_instance.action == data_diff.action
                assert data_diff_instance.label.action == data_diff.label.action
                assert data_diff_instance.file.action == data_diff.file.action
                assert data_diff_instance.remote_path == data_diff.remote_path
        assert segment_diff_generator.value == segment_diffs["totalCount"]
        open_api_do.assert_called_once_with(
            "GET", f"diffs/{basehead}/segments", self.dataset_client._dataset_id, params=params
        )
        list_data_diffs.assert_called_once_with(basehead, "test_segment")

    def test__generate_data_diffs(self, mocker):
        params = {"offset": 0, "limit": 128}
        basehead = "commit-fc2cf9f910b7446aaccc7b833fe4e178"
        segment_name = "test_segment"
        data_diffs = {
            "data": [
                {
                    "remotePath": "1629800110640323954/3.png",
                    "action": "add",
                    "file": {"action": "add"},
                    "label": {"action": ""},
                },
                {
                    "remotePath": "1629800110640323954/4.png",
                    "action": "add",
                    "file": {"action": "add"},
                    "label": {"action": ""},
                },
            ],
            "totalCount": 2,
        }
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=data_diffs),
        )
        data_diff_generator = ReturnGenerator(
            self.dataset_client._generate_data_diffs(basehead, segment_name)
        )
        for data_diff_instance, data_diff in zip(data_diff_generator, data_diffs["data"]):
            assert data_diff_instance.action == data_diff["action"]
            assert data_diff_instance.label.action == data_diff["label"]["action"]
            assert data_diff_instance.file.action == data_diff["file"]["action"]
            assert data_diff_instance.remote_path == data_diff["remotePath"]
        assert data_diff_generator.value == data_diffs["totalCount"]
        open_api_do.assert_called_once_with(
            "GET",
            f"diffs/{basehead}/segments/{segment_name}/data",
            self.dataset_client._dataset_id,
            params=params,
        )

    def test__upload_segment(self, mocker):
        segment_test = Segment(name="test1")
        for i in range(5):
            segment_test.append(Data(f"data{i}.png"))
        segment_client = SegmentClient(name="test1", data_client=self.dataset_client)
        get_or_create_segment = mocker.patch(
            f"{dataset.__name__}.DatasetClient.get_or_create_segment", return_value=segment_client
        )
        list_data_paths = mocker.patch(
            f"{segment.__name__}.SegmentClient.list_data_paths",
            return_value=["data1.png", "data2.png"],
        )
        multithread_upload = mocker.patch(f"{dataset.__name__}.multithread_upload")

        with Tqdm(5, disable=False) as pbar:
            self.dataset_client._upload_segment(segment_test, skip_uploaded_files=True, pbar=pbar)
            get_or_create_segment.assert_called_once_with(segment_test.name)
            list_data_paths.assert_called_once_with()
            args, keywords = multithread_upload.call_args
            assert args[0] == segment_client._upload_or_import_data
            assert [item.path for item in args[1]] == ["data0.png", "data3.png", "data4.png"]
            assert keywords["callback"] == segment_client._synchronize_upload_info
            assert keywords["jobs"] == 1
            assert keywords["pbar"] == pbar
            multithread_upload.assert_called_once()
        with Tqdm(5, disable=False) as pbar:
            self.dataset_client._upload_segment(segment_test, skip_uploaded_files=False, pbar=pbar)
            get_or_create_segment.assert_called_with(segment_test.name)
            list_data_paths.assert_called_with()
            args, keywords = multithread_upload.call_args
            assert args[0] == segment_client._upload_or_import_data
            assert [item.path for item in args[1]] == [f"data{i}.png" for i in range(5)]
            assert keywords["callback"] == segment_client._synchronize_upload_info
            assert keywords["jobs"] == 1
            assert keywords["pbar"] == pbar
            multithread_upload.assert_called()

    def test_get_or_create_segment(self, mocker):
        self.dataset_client._status.checkout(draft_number=1)
        list_segment = mocker.patch(
            f"{dataset.__name__}.DatasetClient.list_segment_names", return_value=["test1"]
        )
        create_segment = mocker.patch(
            f"{dataset.__name__}.DatasetClient._create_segment",
        )
        segment_client_1 = self.dataset_client.get_or_create_segment("test1")
        list_segment.assert_called_once_with()
        assert segment_client_1.name == "test1"
        segment_client_2 = self.dataset_client.get_or_create_segment("test2")
        list_segment.assert_called_with()
        create_segment.assert_called_once_with("test2")
        assert segment_client_2.name == "test2"

    def test_create_segment(self, mocker):
        self.dataset_client._status.checkout(draft_number=1)
        list_segment = mocker.patch(
            f"{dataset.__name__}.DatasetClient.list_segment_names", return_value=["test1"]
        )
        create_segment = mocker.patch(
            f"{dataset.__name__}.DatasetClient._create_segment",
        )
        with pytest.raises(NameConflictError):
            self.dataset_client.create_segment("test1")
            list_segment.assert_called_once_with()
        segment_client = self.dataset_client.create_segment("test2")
        list_segment.assert_called_with()
        create_segment.assert_called_once_with("test2")
        assert segment_client.name == "test2"

    def test_copy_segment(self, mocker):
        self.dataset_client._status.checkout(draft_number=1)
        source_name, target_name = "default", "train"
        copy_segment = mocker.patch(f"{dataset.__name__}.DatasetClient._copy_segment")
        strategy = "abort"
        assert self.dataset_client.copy_segment(source_name).name == source_name
        copy_segment.assert_called_once_with(
            source_name, source_name, source_client=None, strategy=strategy
        )
        strategy = "override"
        assert (
            self.dataset_client.copy_segment(source_name, target_name, strategy=strategy).name
            == target_name
        )
        copy_segment.assert_called_with(
            source_name, target_name, source_client=None, strategy=strategy
        )

    def test_move_segment(self, mocker):
        self.dataset_client._status.checkout(draft_number=1)
        source_name, target_name = "default", "train"
        move_segment = mocker.patch(f"{dataset.__name__}.DatasetClient._move_segment")
        strategy = "abort"
        assert self.dataset_client.move_segment(source_name, target_name).name == target_name
        move_segment.assert_called_once_with(source_name, target_name, strategy=strategy)

    def test_get_segment(self, mocker):
        list_segment = mocker.patch(
            f"{dataset.__name__}.DatasetClient.list_segment_names", return_value=["test1"]
        )
        with pytest.raises(ResourceNotExistError):
            self.dataset_client.get_segment("test2")
            list_segment.assert_called_once_with()
        assert self.dataset_client.get_segment("test1").name == "test1"
        list_segment.assert_called_with()

    def test_upload_segment(self, mocker):
        self.dataset_client._status.checkout(draft_number=1)
        segment_test = Segment(name="test1")
        for i in range(5):
            segment_test.append(Data(f"data{i}.png"))
        segment_client = SegmentClient(name="test1", data_client=self.dataset_client)
        upload_segment = mocker.patch(
            f"{dataset.__name__}.DatasetClient._upload_segment", return_value=segment_client
        )
        assert self.dataset_client.upload_segment(segment_test).name == "test1"
        args, keywords = upload_segment.call_args
        assert args[0] == segment_test
        assert keywords["jobs"] == 1
        assert not keywords["skip_uploaded_files"]
        upload_segment.assert_called_once()

    @staticmethod
    def _mock_generate_segment_diffs():
        segment_diffs = {
            "segments": [
                {
                    "name": "test_segment",
                    "action": "modify",
                    "data": {
                        "stats": {"total": 2, "additions": 2, "deletions": 0, "modifications": 0}
                    },
                    "sensor": {"action": ""},
                }
            ],
            "totalCount": 1,
        }
        data_diffs = [
            DataDiff.loads(
                {
                    "remotePath": "1629800110640323954/3.png",
                    "action": "add",
                    "file": {"action": "add"},
                    "label": {"action": ""},
                }
            ),
            DataDiff.loads(
                {
                    "remotePath": "1629800110640323954/4.png",
                    "action": "add",
                    "file": {"action": "add"},
                    "label": {"action": ""},
                }
            ),
        ]
        for segment_diff_response in segment_diffs["segments"]:
            segment_name = segment_diff_response["name"]
            segment_diff = SegmentDiff(segment_name, segment_diff_response["action"], data_diffs)
            yield segment_diff

        return segment_diffs["totalCount"]

    def test_get_diff(self, mocker):
        basehead = "commit-fc2cf9f910b7446aaccc7b833fe4e178"
        get_basehead = mocker.patch(
            f"{dataset.__name__}.DatasetClient._get_basehead", return_value=basehead
        )
        generate_segment_diffs = mocker.patch(
            f"{dataset.__name__}.DatasetClient._generate_segment_diffs",
            return_value=self._mock_generate_segment_diffs(),
        )
        dataset_diff = self.dataset_client.get_diff()
        assert dataset_diff.name == "test_dataset"
        get_basehead.assert_called_once_with(None, None)
        generate_segment_diffs.assert_called_once_with(basehead, 0, 128)


class TestFusionDatasetClient(TestDatasetClientBase):
    gas_client = GAS("Accesskey-********************************")
    fusion_dataset_client = FusionDatasetClient(
        "test_dataset",
        "12345",
        gas_client,
        status=Status(DEFAULT_BRANCH, commit_id=ROOT_COMMIT_ID),
    )
    source_dataset_client = FusionDatasetClient(
        "source_dataset",
        "544321",
        gas_client,
        status=Status(DEFAULT_BRANCH, commit_id=ROOT_COMMIT_ID),
    )

    def test__extract_all_data(self):
        source_frames = []
        ulids = []
        for i in range(5):
            temp_frame = Frame()
            if i % 2 == 0:
                temp_frame["camera"] = Data(f"{i}.png")
            else:
                temp_frame["lidar"] = Data(f"{i}.png")
            temp_ulid = from_timestamp(10 * i + 10)
            temp_frame.frame_id = temp_ulid
            source_frames.append((temp_frame, temp_ulid))
            ulids.append(temp_ulid)

        with Tqdm(5, disable=False) as pbar:
            for index, values in enumerate(
                self.fusion_dataset_client._extract_all_data(source_frames, pbar)
            ):
                data, sensor_name, frame_id = values
                assert data.path == f"{index}.png"
                if index % 2 == 0:
                    assert sensor_name == "camera"
                else:
                    assert sensor_name == "lidar"
                assert frame_id == ulids[index].str

    def test__extract_unuploaded_data(self):
        source_frames = []
        ulids = []
        done_frames = {}
        for i in range(5):
            temp_frame = Frame()
            temp_ulid = from_timestamp(10 * i + 10)
            if i % 2 == 0:
                temp_frame["camera"] = Data(f"{i}.png")
                done_frames[temp_ulid.timestamp().timestamp] = temp_frame
            else:
                temp_frame["lidar"] = Data(f"{i}.png")
                ulids.append(temp_ulid)
            temp_frame.frame_id = temp_ulid
            source_frames.append((temp_frame, temp_ulid))

        with Tqdm(5, disable=False) as pbar:
            for index, values in enumerate(
                self.fusion_dataset_client._extract_unuploaded_data(
                    source_frames, pbar, done_frames=done_frames
                )
            ):
                data, sensor_name, frame_id = values
                assert data.path == f"{index * 2 + 1}.png"
                assert sensor_name == "lidar"
                assert frame_id == ulids[index].str

    def test__generate_segments(self, mocker):
        params = self.dataset_client._status.get_status_info()
        offset, limit = 0, 128
        params["offset"] = offset
        params["limit"] = limit
        response_data = {
            "offset": 0,
            "recordSize": 2,
            "totalCount": 2,
            "segments": [
                {"name": "test", "description": ""},
                {"name": "train", "description": ""},
            ],
        }
        list_segments = mocker.patch(
            f"{dataset.__name__}.FusionDatasetClient._list_segments",
            return_value=response_data,
        )
        segment_generator = ReturnGenerator(self.fusion_dataset_client._generate_segments())
        assert [segment.name for segment in segment_generator] == [
            item["name"] for item in response_data["segments"]
        ]
        list_segments.assert_called_once_with(offset, limit)
        assert segment_generator.value == response_data["totalCount"]

    def test__upload_segment(self, mocker):
        segment_test = FusionSegment(name="test1")
        ulids = []
        done_frames = []
        for i in range(5):
            temp_frame = Frame()
            temp_ulid = from_timestamp(10 * i + 10)
            temp_frame.frame_id = temp_ulid
            if i % 2 == 0:
                temp_frame["camera"] = Data(f"{i}.png")
                done_frames.append(temp_frame)
            else:
                temp_frame["lidar"] = Data(f"{i}.png")
            ulids.append(temp_ulid)
            segment_test.append(temp_frame)

        segment_client = FusionSegmentClient(name="test1", data_client=self.fusion_dataset_client)
        get_or_create_segment = mocker.patch(
            f"{dataset.__name__}.FusionDatasetClient.get_or_create_segment",
            return_value=segment_client,
        )

        list_frames = mocker.patch(
            f"{segment.__name__}.FusionSegmentClient.list_frames",
            return_value=done_frames,
        )

        multithread_upload = mocker.patch(f"{dataset.__name__}.multithread_upload")

        with Tqdm(5, disable=False) as pbar:
            self.fusion_dataset_client._upload_segment(
                segment_test, jobs=8, skip_uploaded_files=True, pbar=pbar
            )
            get_or_create_segment.assert_called_once_with(segment_test.name)
            list_frames.assert_called_once_with()
            args, keywords = multithread_upload.call_args
            for index, values in enumerate(args[1]):
                data, sensor_name, frame_id = values
                assert data.path == f"{index * 2 + 1}.png"
                assert sensor_name == "lidar"
                assert frame_id == ulids[index * 2 + 1].str
            assert keywords["callback"] == segment_client._synchronize_upload_info
            assert keywords["jobs"] == 8
            assert keywords["pbar"] == pbar
            multithread_upload.assert_called_once()
        with Tqdm(5, disable=False) as pbar:
            self.fusion_dataset_client._upload_segment(
                segment_test, jobs=8, skip_uploaded_files=False, pbar=pbar
            )
            get_or_create_segment.assert_called_with(segment_test.name)
            list_frames.assert_called_with()
            args, keywords = multithread_upload.call_args
            for index, values in enumerate(args[1]):
                data, sensor_name, frame_id = values
                assert data.path == f"{index}.png"
                if index % 2 == 0:
                    assert sensor_name == "camera"
                else:
                    assert sensor_name == "lidar"
                assert frame_id == ulids[index].str
            assert keywords["callback"] == segment_client._synchronize_upload_info
            assert keywords["jobs"] == 8
            assert keywords["pbar"] == pbar

    def test_get_or_create_segment(self, mocker):
        self.fusion_dataset_client._status.checkout(draft_number=1)
        list_segment = mocker.patch(
            f"{dataset.__name__}.FusionDatasetClient.list_segment_names", return_value=["test1"]
        )
        create_segment = mocker.patch(
            f"{dataset.__name__}.FusionDatasetClient._create_segment",
        )
        segment_client_1 = self.fusion_dataset_client.get_or_create_segment("test1")
        list_segment.assert_called_once_with()
        assert segment_client_1.name == "test1"
        segment_client_2 = self.fusion_dataset_client.get_or_create_segment("test2")
        list_segment.assert_called_with()
        create_segment.assert_called_once_with("test2")
        assert segment_client_2.name == "test2"

    def test_create_segment(self, mocker):
        self.fusion_dataset_client._status.checkout(draft_number=1)
        list_segment = mocker.patch(
            f"{dataset.__name__}.FusionDatasetClient.list_segment_names", return_value=["test1"]
        )
        create_segment = mocker.patch(
            f"{dataset.__name__}.FusionDatasetClient._create_segment",
        )
        with pytest.raises(NameConflictError):
            self.fusion_dataset_client.create_segment("test1")
            list_segment.assert_called_once_with()
        segment_client = self.fusion_dataset_client.create_segment("test2")
        list_segment.assert_called_with()
        create_segment.assert_called_once_with("test2")
        assert segment_client.name == "test2"

    def test_copy_segment(self, mocker):
        self.fusion_dataset_client._status.checkout(draft_number=1)
        source_name, target_name = "default", "train"
        copy_segment = mocker.patch(f"{dataset.__name__}.FusionDatasetClient._copy_segment")
        strategy = "abort"
        assert self.fusion_dataset_client.copy_segment(source_name).name == source_name
        copy_segment.assert_called_once_with(
            source_name, source_name, source_client=None, strategy=strategy
        )
        strategy = "override"
        assert (
            self.fusion_dataset_client.copy_segment(
                source_name, target_name, strategy=strategy
            ).name
            == target_name
        )
        copy_segment.assert_called_with(
            source_name, target_name, source_client=None, strategy=strategy
        )

    def test_move_segment(self, mocker):
        self.fusion_dataset_client._status.checkout(draft_number=1)
        source_name, target_name = "default", "train"
        move_segment = mocker.patch(f"{dataset.__name__}.FusionDatasetClient._move_segment")
        strategy = "abort"
        assert self.fusion_dataset_client.move_segment(source_name, target_name).name == target_name
        move_segment.assert_called_once_with(source_name, target_name, strategy=strategy)

    def test_get_segment(self, mocker):
        list_segment = mocker.patch(
            f"{dataset.__name__}.FusionDatasetClient.list_segment_names", return_value=["test1"]
        )
        with pytest.raises(ResourceNotExistError):
            self.fusion_dataset_client.get_segment("test2")
            list_segment.assert_called_once_with()
        assert self.fusion_dataset_client.get_segment("test1").name == "test1"
        list_segment.assert_called_with()

    def test_upload_segment(self, mocker):
        self.fusion_dataset_client._status.checkout(draft_number=1)
        segment_test = FusionSegment(name="test1")
        for i in range(5):
            temp_frame = Frame()
            temp_ulid = from_timestamp(10 * i + 10)
            temp_frame.frame_id = temp_ulid
            if i % 2 == 0:
                temp_frame["camera"] = Data(f"{i}.png")
            else:
                temp_frame["lidar"] = Data(f"{i}.png")
            segment_test.append(temp_frame)

        segment_client = FusionSegmentClient(name="test1", data_client=self.fusion_dataset_client)
        upload_segment = mocker.patch(
            f"{dataset.__name__}.FusionDatasetClient._upload_segment", return_value=segment_client
        )
        assert self.fusion_dataset_client.upload_segment(segment_test).name == "test1"
        args, keywords = upload_segment.call_args
        assert args[0] == segment_test
        assert keywords["jobs"] == 1
        assert not keywords["skip_uploaded_files"]
        upload_segment.assert_called_once()
