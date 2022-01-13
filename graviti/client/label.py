#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Interfaces about the label."""

from typing import Any, Dict, Optional


def get_label_statistics(  # pylint: disable=unused-argument
    url: str,
    access_key: str,
    dataset_id: str,
    *,
    draft_number: Optional[int] = None,
    commit: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute the OpenAPI `GET /v1/datasets{id}/labels/statistics`.

    Arguments:
        url: The URL of the graviti website.
        access_key: User's access key.
        dataset_id: Dataset ID.
        draft_number: The draft number.
        commit: The information to locate the specific commit, which can be the commit id,
            the branch name, or the tag name.

    Return:
        The response of OpenAPI.

    """
