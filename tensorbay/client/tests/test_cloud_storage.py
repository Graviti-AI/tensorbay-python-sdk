#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import os

import pytest

from ...dataset import Dataset
from ...exception import DatasetTypeError, ResourceNotExistError
from .. import gas
from ..cloud_storage import CloudClient
from ..dataset import DatasetClient, FusionDatasetClient
from ..gas import DEFAULT_BRANCH, GAS
from ..requests import Client
from ..status import Status
from ..struct import ROOT_COMMIT_ID, Draft
from .utility import mock_response


class TestCloudClient:
    client = Client("Accesskey-********************************")
    cloud_client = CloudClient("auth_config", client)

    def test_list_files(self, mocker):
        params = {
            "prefix": "cloud_path",
            "limit": 128,
        }
        response_data = {
            "cloudFiles": [
                "cloud_path/file1.jpg",
                "cloud_path/file2.jpg",
            ],
            "truncated": 0,
            "nextMarker": "",
        }
        open_api_do = mocker.patch(
            f"{gas.__name__}.Client.open_api_do",
            return_value=mock_response(data=response_data),
        )
        assert self.cloud_client.list_files(params["prefix"]) == response_data["cloudFiles"]
        open_api_do.assert_called_once_with(
            "GET", f"cloud/{self.cloud_client._name}/files", params=params
        )
