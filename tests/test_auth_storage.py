#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay import GAS
from tensorbay.dataset import Data, Dataset, Frame, FusionDataset, FusionSegment, Segment
from tensorbay.exception import ResourceNotExistError
from tensorbay.label import Catalog, Classification, Label
from tensorbay.sensor import Lidar
from tests.test_upload import CATALOG, LABEL
from tests.utility import get_dataset_name

_LOCAL_CONFIG_NAME = "HDFS_本地1"


class TestCloudStorage:
    @pytest.mark.parametrize("config_name", ["azure_china_config", "oss_config", "s3_config"])
    def test_create_dataset_with_config(self, accesskey, url, config_name):
        gas_client = GAS(access_key=accesskey, url=url)
        try:
            gas_client.get_cloud_client(config_name)
        except ResourceNotExistError:
            pytest.skip(f"skip this case because there's no {config_name} config")

        dataset_name = get_dataset_name()
        gas_client.create_dataset(dataset_name, config_name=config_name)
        gas_client.get_dataset(dataset_name)

        gas_client.delete_dataset(dataset_name)

    @pytest.mark.parametrize("config_name", ["azure_china_config", "oss_config", "s3_config"])
    def test_import_cloud_files_to_dataset(self, accesskey, url, config_name):

        gas_client = GAS(access_key=accesskey, url=url)
        try:
            cloud_client = gas_client.get_cloud_client(config_name)
        except ResourceNotExistError:
            pytest.skip(f"skip this case because there's no {config_name} config")

        auth_data = cloud_client.list_auth_data("tests")
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, config_name=config_name)

        dataset = Dataset(name=dataset_name)
        segment = dataset.create_segment("Segment1")
        for data in auth_data:
            data.label.classification = Classification("cat", attributes={"color": "red"})
            segment.append(data)

        dataset_client = gas_client.upload_dataset(dataset, jobs=5)
        dataset_client.commit("import data")

        segment1 = Segment("Segment1", client=dataset_client)
        assert len(segment1) == len(segment)
        assert segment1[0].path == segment[0].path.split("/")[-1]
        assert segment1[0].label.classification.category == "cat"
        assert segment1[0].label.classification.attributes["color"] == "red"

        assert len(auth_data) == len(segment)

        gas_client.delete_dataset(dataset_name)

    @pytest.mark.parametrize("config_name", ["azure_china_config", "oss_config", "s3_config"])
    def test_import_cloud_files_to_fusiondataset(self, accesskey, url, config_name):
        gas_client = GAS(access_key=accesskey, url=url)
        try:
            cloud_client = gas_client.get_cloud_client(config_name)
        except ResourceNotExistError:
            pytest.skip(f"skip this case because there's no {config_name} config")

        auth_data = cloud_client.list_auth_data("tests")[:5]
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name, True, config_name=config_name)

        dataset = FusionDataset(name=dataset_name)
        segment = dataset.create_segment("Segment1")
        lidar = Lidar("LIDAR")
        segment.sensors.add(lidar)

        for data in auth_data:
            data.label.classification = Classification("cat", attributes={"color": "red"})
            frame = Frame()
            frame["LIDAR"] = data
            segment.append(frame)

        dataset_client = gas_client.upload_dataset(dataset, jobs=5)
        dataset_client.commit("import data")

        segment1 = FusionSegment("Segment1", client=dataset_client)
        assert len(segment1) == len(segment)
        assert segment1[0]["LIDAR"].path == segment[0]["LIDAR"].path.split("/")[-1]
        assert segment1[0]["LIDAR"].label.classification.category == "cat"
        assert segment1[0]["LIDAR"].label.classification.attributes["color"] == "red"
        assert len(auth_data) == len(segment)

        gas_client.delete_dataset(dataset_name)


class TestLocalStorage:
    def test_create_and_upload_dataset_with_config(self, accesskey, url, tmp_path):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        try:
            gas_client.get_auth_storage_config(name=_LOCAL_CONFIG_NAME)
        except ResourceNotExistError:
            pytest.skip(f"skip this case because there's no {_LOCAL_CONFIG_NAME} config")

        gas_client.create_dataset(dataset_name, config_name=_LOCAL_CONFIG_NAME)
        dataset = Dataset(name=dataset_name)
        segment = dataset.create_segment("Segment1")
        # When uploading label, upload catalog first.
        dataset._catalog = Catalog.loads(CATALOG)

        path = tmp_path / "sub"
        path.mkdir()
        for i in range(5):
            local_path = path / f"hello{i}.txt"
            local_path.write_text("CONTENT")
            data = Data(local_path=str(local_path))
            data.label = Label.loads(LABEL)
            segment.append(data)

        dataset_client = gas_client.upload_dataset(dataset)
        assert dataset_client.get_catalog()
        segment1 = Segment("Segment1", client=dataset_client)
        assert len(segment1) == 5
        for i in range(5):
            assert segment1[i].path == f"hello{i}.txt"
            assert segment1[i].label

        gas_client.delete_dataset(dataset_name)

    def test_create_local_storage_config(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        local_storage_name = "local_storage_config"
        local_storage = {
            "name": local_storage_name,
            "file_path": "file_path/",
            "endpoint": "http://192.168.0.1:9000",
        }
        gas_client.create_local_storage_config(**local_storage)
        gas_client.delete_storage_config(local_storage_name)
