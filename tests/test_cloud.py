#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay import GAS
from tensorbay.dataset import Dataset, Segment
from tensorbay.exception import ResourceNotExistError

from .utility import get_dataset_name


class TestImportData:
    @pytest.mark.parametrize("config_name", ["azure_china_config", "oss_config", "s3_config"])
    def test_import_cloud_files(self, accesskey, url, config_name):

        gas_client = GAS(access_key=accesskey, url=url)
        try:
            cloud_client = gas_client.get_cloud_client(config_name)
        except ResourceNotExistError:
            pytest.skip(f"skip this case because there's no {config_name} config")

        auth_data = cloud_client.list_auth_data("tests")
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_auth_dataset(dataset_name, config_name)

        dataset = Dataset(name=dataset_name)
        segment = dataset.create_segment("Segment1")
        for data in auth_data:
            segment.append(data)

        dataset_client = gas_client.upload_dataset(dataset, jobs=5)
        dataset_client.commit("import data")

        segment1 = Segment("Segment1", client=dataset_client)
        assert len(segment1) == len(segment)
        assert segment1[0].path == segment[0].path.split("/")[-1]
        assert not segment1[0].label

        assert len(auth_data) == len(segment)

        gas_client.delete_dataset(dataset_name)
