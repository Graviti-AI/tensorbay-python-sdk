#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=pointless-string-statement
# pylint: disable=invalid-name
"""This file includes the python code of auth cloud storage import."""

"""Get cloud client"""
from tensorbay import GAS

# Please visit `https://gas.graviti.com/tensorbay/developer` to get the AccessKey.
gas = GAS("<YOUR_ACCESSKEY>")
cloud_client = gas.get_cloud_client("<CONFIG_NAME>")
""""""

"""Create storage config"""
gas.create_oss_storage_config(
    "<OSS_CONFIG_NAME>",
    "<path/to/dataset>",
    endpoint="<YOUR_ENDPOINT>",  # like oss-cn-qingdao.aliyuncs.com
    accesskey_id="<YOUR_ACCESSKEYID>",
    accesskey_secret="<YOUR_ACCESSKEYSECRET>",
    bucket_name="<YOUR_BUCKETNAME>",
)
""""""

"""Import dataset from cloud platform to the authorized storage dataset"""
import json

from tensorbay.dataset import Dataset
from tensorbay.label import Classification

# Use AuthData to organize a dataset by the "Dataset" class before importing.
dataset = Dataset("<DATASET_NAME>")

# TensorBay uses "segment" to separate different parts in a dataset.
segment = dataset.create_segment()

images = cloud_client.list_auth_data("<data/images/>")
labels = cloud_client.list_auth_data("<data/labels/>")

for auth_data, label in zip(images, labels):
    with label.open() as fp:
        auth_data.label.classification = Classification.loads(json.load(fp))
    segment.append(auth_data)

dataset_client = gas.upload_dataset(dataset, jobs=8)
""""""


"""Create local storage config"""
gas.create_local_storage_config(
    name="<LOCAL_STORAGE_CONFIG>",
    file_path="<path/to/dataset>",
    endpoint="<external IP address of the local storage service>",
)
""""""

"""Create authorized local storage dataset"""
dataset_client = gas.create_dataset("<DATASET_NAME>", config_name="<LOCAL_STORAGE_CONFIG>")
""""""
