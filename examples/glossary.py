#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=pointless-string-statement
# pylint: disable=missing-function-docstring
# pylint: disable=unused-argument
# pylint: disable=invalid-name

"""This files includes the python code example in glossary.rst."""

"""dataloader"""
from tensorbay.dataset import Dataset


def DatasetName(path: str) -> Dataset:
    """The dataloader of <Dataset Name>  dataset.

    Arguments:
        path: The root directory of the dataset.
            The file structure should be like::

                <path>
                    structure under the path

    Returns:
        The loaded 'Dataset' object.

    """
    dataset = Dataset("<Dataset Name>")
    ...  # organize the files( and the labels) under the path to the dataset
    return dataset


""""""
