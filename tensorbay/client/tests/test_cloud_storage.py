#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from itertools import zip_longest

from ...dataset import AuthData
from .. import gas
from ..cloud_storage import CloudClient
from ..requests import Client
from .utility import mock_response


class TestCloudClient:
    client = Client("Accesskey-********************************")
    cloud_client = CloudClient("auth_config", client)

    def test_list_auth_data(self, mocker):
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
        for auth_data, cloud_path in zip_longest(
            self.cloud_client.list_auth_data(params["prefix"]), response_data["cloudFiles"]
        ):
            assert isinstance(auth_data, AuthData)
            assert auth_data.path == cloud_path
        open_api_do.assert_called_once_with(
            "GET", f"cloud/{self.cloud_client._name}/files", params=params
        )
