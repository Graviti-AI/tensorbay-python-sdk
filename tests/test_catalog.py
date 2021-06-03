#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay import GAS
from tensorbay.exception import StatusError
from tensorbay.label import Catalog

from .utility import get_dataset_name

CATALOG = {
    "BOX2D": {
        "categories": [
            {"name": "01"},
            {"name": "02"},
            {"name": "03"},
            {"name": "04"},
            {"name": "05"},
            {"name": "06"},
            {"name": "07"},
            {"name": "08"},
            {"name": "09"},
            {"name": "10"},
            {"name": "11"},
            {"name": "12"},
            {"name": "13"},
            {"name": "14"},
            {"name": "15"},
        ],
        "attributes": [
            {"name": "Vertical angle", "enum": [-90, -60, -30, -15, 0, 15, 30, 60, 90]},
            {
                "name": "Horizontal angle",
                "enum": [-90, -75, -60, -45, -30, -15, 0, 15, 30, 45, 60, 75, 90],
            },
            {"name": "Serie", "enum": [1, 2]},
            {"name": "Number", "type": "integer", "minimum": 0, "maximum": 92},
        ],
    }
}


class TestCatalog:
    def test_catalog(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)

        with pytest.raises(StatusError):
            dataset_client.upload_catalog(Catalog.loads(CATALOG))
        dataset_client.create_draft("draft-1")
        dataset_client.upload_catalog(Catalog.loads(CATALOG))
        catalog = dataset_client.get_catalog()
        # todo: match the input and output catalog

        gas_client.delete_dataset(dataset_name)
