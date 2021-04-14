#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Exceptions about open data loader.

The content in this module is deprecated since v1.3.0, and will be removed in v1.5.0.

Please use :class:`~tensorbay.exception.NoFileError` instead of :class:`OpenDatasetNoFileError`.

"""

from ...exception import NoFileError

OpenDatasetNoFileError = NoFileError
