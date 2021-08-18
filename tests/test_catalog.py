#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay import GAS
from tensorbay.exception import InvalidParamsError
from tensorbay.label import Catalog

from .utility import get_dataset_name

CATALOG1 = {
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


CATALOG2 = {
    "BOX2D": {
        "categories": [
            {"name": "01"},
            {"name": "02"},
            {"name": "03"},
            {"name": "04"},
            {"name": "05"},
        ],
        "attributes": [
            {"name": "Vertical angle", "enum": [-90, -60, -30, -15, 0, 15, 30, 60, 90]},
            {
                "name": "Horizontal angle",
                "enum": [-90, -75, -60, -45, -30, -15, 0, 15, 30, 45, 60, 75, 90],
            },
            {"name": "Serie", "enum": [1, 2]},
        ],
    }
}


class TestCatalog:
    def test_first_upload_catalog(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        catalog_to_upload = Catalog.loads(CATALOG1)
        dataset_client.create_draft("draft-1")

        dataset_client.upload_catalog(catalog_to_upload)
        catalog_get = dataset_client.get_catalog()
        assert catalog_get == catalog_to_upload

        gas_client.delete_dataset(dataset_name)

    def test_modify_catalog(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        dataset_client.create_draft("draft-1")
        dataset_client.upload_catalog(Catalog.loads(CATALOG2))

        catalog_to_upload = Catalog.loads(CATALOG2)
        dataset_client.upload_catalog(catalog_to_upload)
        catalog_get = dataset_client.get_catalog()
        assert catalog_get == catalog_to_upload

        # Uploading empty catalog is not allowed
        catalog_to_upload = Catalog.loads({})
        with pytest.raises(InvalidParamsError):
            dataset_client.upload_catalog(catalog_to_upload)

        gas_client.delete_dataset(dataset_name)

    def test_catalog_version_control(self, accesskey, url):
        gas_client = GAS(access_key=accesskey, url=url)
        dataset_name = get_dataset_name()
        dataset_client = gas_client.create_dataset(dataset_name)
        catalog_to_upload = Catalog.loads(CATALOG1)
        dataset_client.create_draft("draft-1")
        dataset_client.upload_catalog(catalog_to_upload)

        # After committing the draft, catalog is stored in the new commit
        dataset_client.commit("commit-1")
        catalog_get_commit = dataset_client.get_catalog()
        assert catalog_get_commit == catalog_to_upload

        # After creating a new draft, catalog is stored in the new draft
        dataset_client.create_draft("draft-2")
        catalog_get_draft = dataset_client.get_catalog()
        assert catalog_get_draft == catalog_to_upload

        gas_client.delete_dataset(dataset_name)
