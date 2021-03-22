#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from .. import Classification

_CATEGORY = "test"
_ATTRIBUTES = {"key": "value"}

_CLASSIFICATION_DATA = {"category": "test", "attributes": {"key": "value"}}


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
