#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=not-callable
# pylint: disable=ungrouped-imports
# pylint: disable=import-error
# pylint: disable=pointless-string-statement
# pylint: disable=invalid-name


"""This file includes the python code of visualization.rst."""

"""Organize a Dataset"""
from tensorbay.opendataset import BSTLD

dataset = BSTLD("path/to/dataset")
""""""

"""Visualize The Dataset"""
from pharos import visualize

visualize(dataset)
""""""
