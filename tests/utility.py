#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Utility method for integration test."""

import uuid
from typing import Iterator

from tensorbay.client.struct import Draft


def get_random_dataset_name() -> str:
    """Get the random dataset name.

    Returns:
        A random dataset name.

    """
    return f"test{uuid.uuid4().hex}"


def get_draft_number_by_title(drafts: Iterator[Draft], title: str) -> int:
    """Get the draft number with the given draft title.

    Arguments:
        drafts: All the drafts.
        title: The given draft title.

    Returns:
        The draft number.

    Raises:
        TypeError: When find no draft with the given name.

    """
    for draft in drafts:
        if title == draft.title:
            return draft.number

    raise TypeError("Cannot find the draft with the given name.")
