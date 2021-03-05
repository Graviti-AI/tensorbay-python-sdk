#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from .. import Data, Segment


class TestSegment:
    def test_sort(self):
        segment = Segment("train")
        segment.append(Data("file1"))
        segment.append(Data("file2"))

        assert segment[0].path == "file1"

        segment.sort(key=lambda data: data.path, reverse=True)
        assert segment[0].path == "file2"
