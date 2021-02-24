#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#

"""This file defines the glob method for open dataset."""

from glob import glob as buildin_glob
from typing import List

from .exceptions import OpenDatasetNoFileError


def glob(pathname: str, *, recursive: bool = False) -> List[str]:
    """
    Return a sorted list of paths matching a pathname pattern.
    If the result list is empty, raise `OpenDatasetNoFileError`

    The pattern may contain simple shell-style wildcards a la
    fnmatch. However, unlike fnmatch, filenames starting with a
    dot are special cases that are not matched by '*' and '?'
    patterns.

    :param pathname: the pathname pattern
    :param recursive: if recursive is true, the pattern '**' will match any files and
    zero or more directories and subdirectories.

    :return: a sorted list of paths matching a pathname pattern
    :raises OpenDatasetNoFileError: when there is no file matching the given pathname pattern
    """

    paths = buildin_glob(pathname, recursive=recursive)
    if not paths:
        raise OpenDatasetNoFileError(pathname)
    paths.sort()

    return paths
