#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""This file defines the glob method for open dataset."""

from glob import glob as buildin_glob
from typing import List

from ...exception import NoFileError


def glob(pathname: str, *, recursive: bool = False) -> List[str]:
    """Return a sorted list of paths matching a pathname pattern.

    The pattern may contain simple shell-style wildcards a la fnmatch.
    However, unlike fnmatch, filenames starting with a dot are special cases
    that are not matched by '*' and '?' patterns.

    Arguments:
        pathname: The pathname pattern.
        recursive: If recursive is true, the pattern '**' will match any files and
            zero or more directories and subdirectories.

    Returns:
        A sorted list of paths matching a pathname pattern.

    Raises:
        NoFileError: When there is no file matching the given pathname pattern.

    """
    paths = buildin_glob(pathname, recursive=recursive)
    if not paths:
        raise NoFileError(pathname)
    paths.sort()

    return paths
