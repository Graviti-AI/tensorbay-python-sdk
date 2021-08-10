#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from ...dataset import Notes
from ...exception import InvalidParamsError, OperationError
from ...label import Catalog
from .. import gas
from ..dataset import DatasetClient
from ..gas import DEFAULT_BRANCH, GAS
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
