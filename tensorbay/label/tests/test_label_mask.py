#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#


import pytest

from ...utility import NameList
from .. import (
    InstanceMask,
    InstanceMaskSubcatalog,
    PanopticMask,
    PanopticMaskSubcatalog,
    SemanticMask,
    SemanticMaskSubcatalog,
)
from ..label_mask import RemoteInstanceMask, RemotePanopticMask, RemoteSemanticMask
from ..supports import MaskCategoryInfo

all_mask_subcatalog = (InstanceMaskSubcatalog, PanopticMaskSubcatalog, SemanticMaskSubcatalog)


@pytest.fixture
def mask_categories(mask_categories_catalog_data):
    category_dict = NameList()
    for category in mask_categories_catalog_data:
        category_dict.append(MaskCategoryInfo.loads(category))
    return category_dict


@pytest.fixture
def subcatalog_contents(mask_categories_catalog_data, attributes_catalog_data):
    return {
        "categories": mask_categories_catalog_data,
        "attributes": attributes_catalog_data,
    }


@pytest.fixture
def mask_file(tmp_path) -> str:
    path = tmp_path / "sub"
    path.mkdir()
    local_path = path / "hello.png"
    local_path.write_text("MASK CONTENT")
    return local_path


class TestMaskSubcatalog:
    """This class used to test three mask subcatalog
    InstanceMaskSubcatalog, PanopticMaskSubcatalog and SemanticMaskSubcatalog
    """

    @pytest.mark.parametrize("SUBCATALOG", all_mask_subcatalog)
    def test_eq(self, SUBCATALOG):
        contents1 = {
            "categories": [{"name": "0", "categoryId": 0}, {"name": "1", "categoryId": 1}],
            "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        }
        contents2 = {
            "categories": [{"name": "0", "categoryId": 1}, {"name": "1", "categoryId": 2}],
            "attributes": [{"name": "gender", "enum": ["male", "female"]}],
        }
        subcatalog1 = SUBCATALOG.loads(contents1)
        subcatalog2 = SUBCATALOG.loads(contents1)
        subcatalog3 = SUBCATALOG.loads(contents2)

        assert subcatalog1 == subcatalog2
        assert subcatalog1 != subcatalog3

    @pytest.mark.parametrize("SUBCATALOG", all_mask_subcatalog)
    def test_loads(self, SUBCATALOG, mask_categories, attributes, subcatalog_contents):
        subcatalog = SUBCATALOG.loads(subcatalog_contents)

        assert subcatalog.categories == mask_categories
        assert subcatalog.attributes == attributes

    @pytest.mark.parametrize("SUBCATALOG", all_mask_subcatalog)
    def test_dumps(self, SUBCATALOG, mask_categories, attributes, subcatalog_contents):
        subcatalog = SUBCATALOG()
        subcatalog.categories = mask_categories
        subcatalog.attributes = attributes
        if isinstance(subcatalog, InstanceMaskSubcatalog):
            subcatalog.is_tracking = False
        assert subcatalog.dumps() == subcatalog_contents


class TestSemanticMask:
    def test_init(self):
        semantic_mask = SemanticMask("semantic_mask.png")
        assert semantic_mask.path == "semantic_mask.png"

    def test_get_callback_body(self, mask_file):
        semantic_mask = SemanticMask(mask_file)
        semantic_mask.all_attributes = {1: {"occluded": True}, 2: {"occluded": False}}
        assert semantic_mask.get_callback_body() == {
            "checksum": "c86aca4e348b051f60c2d7d1bf750fb3accdfeaf",
            "fileSize": 12,
            "info": [
                {"attributes": {"occluded": True}, "categoryId": 1},
                {"attributes": {"occluded": False}, "categoryId": 2},
            ],
        }


class TestInstanceMask:
    def test_init(self):
        instance_mask = InstanceMask("hello.png")
        assert instance_mask.path == "hello.png"

    def test_get_callback_body(self, mask_file):
        instance_mask = InstanceMask(mask_file)
        instance_mask.all_attributes = {1: {"occluded": True}, 2: {"occluded": False}}
        assert instance_mask.get_callback_body() == {
            "checksum": "c86aca4e348b051f60c2d7d1bf750fb3accdfeaf",
            "fileSize": 12,
            "info": [
                {"attributes": {"occluded": True}, "instanceId": 1},
                {"attributes": {"occluded": False}, "instanceId": 2},
            ],
        }


class TestPanopticMask:
    def test_init(self):
        panoptic_mask = PanopticMask("hello.png")
        assert panoptic_mask.path == "hello.png"

    def test_get_callback_body(self, mask_file):
        panoptic_mask = PanopticMask(mask_file)
        panoptic_mask.all_attributes = {1: {"occluded": True}, 2: {"occluded": False}}
        panoptic_mask.all_category_ids = {1: 2, 2: 2}
        assert panoptic_mask.get_callback_body() == {
            "checksum": "c86aca4e348b051f60c2d7d1bf750fb3accdfeaf",
            "fileSize": 12,
            "info": [
                {"attributes": {"occluded": True}, "instanceId": 1, "categoryId": 2},
                {"attributes": {"occluded": False}, "instanceId": 2, "categoryId": 2},
            ],
        }


class TestRemoteSemanticMask:
    def test_from_response_body(self):
        body = {
            "remotePath": "hello.png",
            "info": [
                {"categoryId": 0, "attributes": {"occluded": True}},
                {"categoryId": 1, "attributes": {"occluded": False}},
            ],
        }
        mask = RemoteSemanticMask.from_response_body(body)

        assert mask.path == "hello.png"
        assert mask.all_attributes == {0: {"occluded": True}, 1: {"occluded": False}}


class TestRemoteInstanceMask:
    def test_from_response_body(self):
        body = {
            "remotePath": "hello.png",
            "info": [
                {"instanceId": 0, "attributes": {"occluded": True}},
                {"instanceId": 1, "attributes": {"occluded": False}},
            ],
        }
        mask = RemoteInstanceMask.from_response_body(body)

        assert mask.path == "hello.png"
        assert mask.all_attributes == {0: {"occluded": True}, 1: {"occluded": False}}


class TestRemotePanopticMask:
    def test_from_response_body(self):
        body = {
            "remotePath": "hello.png",
            "info": [
                {"instanceId": 0, "categoryId": 100, "attributes": {"occluded": True}},
                {"instanceId": 1, "categoryId": 101, "attributes": {"occluded": False}},
            ],
        }
        mask = RemotePanopticMask.from_response_body(body)

        assert mask.path == "hello.png"
        assert mask.all_attributes == {0: {"occluded": True}, 1: {"occluded": False}}
        assert mask.all_category_ids == {0: 100, 1: 101}
