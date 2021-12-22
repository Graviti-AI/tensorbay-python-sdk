#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from tensorbay.client import gas
from tensorbay.client.dataset import DatasetClient
from tensorbay.client.gas import DEFAULT_BRANCH, DEFAULT_IS_PUBLIC, GAS
from tensorbay.client.status import Status
from tensorbay.client.struct import ROOT_COMMIT_ID
from tensorbay.client.tests.utility import mock_response


class TestVersionControlMixin:
    gas_client = GAS("Accesskey-********************************")
    dataset_client = DatasetClient(
        "test_dataset",
        "12345",
        gas_client,
        status=Status(DEFAULT_BRANCH, commit_id=ROOT_COMMIT_ID),
        alias="",
        is_public=DEFAULT_IS_PUBLIC,
    )
