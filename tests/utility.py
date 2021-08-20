#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Utility method for integration test."""

from datetime import datetime
from inspect import stack


def get_dataset_name() -> str:
    """Get the random dataset name.

    Returns:
        A random dataset name.

    """
    return f"{stack()[1].function}_{datetime.now().strftime('%Y-%m-%d_%H_%M_%S')}"
