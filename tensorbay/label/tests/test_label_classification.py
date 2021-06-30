#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from .. import Classification, ClassificationSubcatalog


@pytest.fixture
def subcatalog_classification(categories_catalog_data, attributes_catalog_data):
    return {
        "categories": categories_catalog_data,
        "attributes": attributes_catalog_data,
        "categoryDelimiter": ".",
    }


class TestClassification:
    def test_init(self):
        classification = Classification(category="cat", attributes={"gender": "male"})

        assert classification.category == "cat"
        assert classification.attributes == {"gender": "male"}

    def test_eq(self):
        classification1 = Classification("cat", {"gender": "male"})
        classification2 = Classification("cat", {"gender": "male"})
        classification3 = Classification("dog", {"gender": "male"})

        assert classification1 == classification2
        assert classification1 != classification3

    def test_loads(self):
        contents = {"category": "cat", "attributes": {"gender": "male"}}
        classification = Classification.loads(contents)

        assert classification.category == "cat"
        assert classification.attributes == {"gender": "male"}

    def test_dumps(self):
        classification = Classification(category="cat", attributes={"gender": "male"})

        assert classification.dumps() == {"category": "cat", "attributes": {"gender": "male"}}


class TestClassificationSubcatalog:
    def test_init(self):
        description = "This is a test text."
        classification_subcatalog = ClassificationSubcatalog(description)
        classification_subcatalog.description = description

    def test_eq(self):
        contents1 = {"category": "cat", "attributes": [{"name": "color", "enum": ["white", "red"]}]}
        contents2 = {
            "category": "cat",
            "attributes": [{"name": "color", "enum": ["white", "blue"]}],
        }
        classification_subcatalog1 = ClassificationSubcatalog.loads(contents1)
        classification_subcatalog2 = ClassificationSubcatalog.loads(contents1)
        classification_subcatalog3 = ClassificationSubcatalog.loads(contents2)

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
