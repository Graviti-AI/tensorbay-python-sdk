#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from .. import Classification, ClassificationSubcatalog
from ..supports import AttributesMixin, CategoriesMixin

_CATEGORY = "test"
_ATTRIBUTES = {"key": "value"}

_CLASSIFICATION_DATA = {"category": "test", "attributes": {"key": "value"}}


@pytest.fixture
def subcatalog_classification(categories_catalog_data, attributes_catalog_data):
    return {
        "categories": categories_catalog_data,
        "attributes": attributes_catalog_data,
        "categoryDelimiter": ".",
    }


class TestClassification:
    def test_init(self):
        classification = Classification(category=_CATEGORY, attributes=_ATTRIBUTES)

        assert classification.category == _CATEGORY
        assert classification.attributes == _ATTRIBUTES

    def test_eq(self):
        classification1 = Classification("cat", _ATTRIBUTES)
        classification2 = Classification("cat", _ATTRIBUTES)
        classification3 = Classification("dog", _ATTRIBUTES)

        assert classification1 == classification2
        assert classification1 != classification3

    def test_loads(self):
        classification = Classification.loads(_CLASSIFICATION_DATA)

        assert classification.category == _CLASSIFICATION_DATA["category"]
        assert classification.attributes == _CLASSIFICATION_DATA["attributes"]

    def test_dumps(self):
        classification = Classification(category=_CATEGORY, attributes=_ATTRIBUTES)

        assert classification.dumps() == _CLASSIFICATION_DATA


class TestClassificationSubcatalog:
    def test_init_subclass(self):
        classification_subcatalog = ClassificationSubcatalog()
        classification_subcatalog._supports = (CategoriesMixin, AttributesMixin)

    def test_eq(self):
        content1 = {"category": "cat", "attributes": [{"name": "color", "enum": ["white", "red"]}]}
        content2 = {"category": "cat", "attributes": [{"name": "color", "enum": ["white", "blue"]}]}
        classification_subcatalog1 = ClassificationSubcatalog.loads(content1)
        classification_subcatalog2 = ClassificationSubcatalog.loads(content1)
        classification_subcatalog3 = ClassificationSubcatalog.loads(content2)

        assert classification_subcatalog1 == classification_subcatalog2
        assert classification_subcatalog1 != classification_subcatalog3

    def test_loads(self, categories, attributes, subcatalog_classification):
        classification_subcatalog = ClassificationSubcatalog.loads(subcatalog_classification)
        assert classification_subcatalog.categories == categories
        assert classification_subcatalog.attributes == attributes
        assert (
            classification_subcatalog.category_delimiter
            == subcatalog_classification["categoryDelimiter"]
        )

    def test_dumps(self, categories, attributes, subcatalog_classification):
        classification_subcatalog = ClassificationSubcatalog()
        classification_subcatalog.categories = categories
        classification_subcatalog.attributes = attributes
        classification_subcatalog.category_delimiter = subcatalog_classification[
            "categoryDelimiter"
        ]

        assert classification_subcatalog.dumps() == subcatalog_classification
