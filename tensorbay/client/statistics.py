#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""The basic structure of the label statistics."""

from typing import Any, Dict

from tensorbay.utility import UserMapping


class Statistics(UserMapping[str, Any]):
    """This class defines the basic structure of the label statistics.

    Arguments:
        data: The dict containing label statistics.

    """

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data: Dict[str, Any] = data

    def dumps(self) -> Dict[str, Any]:
        """Dumps the label statistics into a dict.

        Returns:
            A dict containing all the information of the label statistics.

        Examples:
            >>> label_statistics = Statistics(
            ...     {
            ...         'BOX3D': {
            ...             'quantity': 1234
            ...         },
            ...         'KEYPOINTS2D': {
            ...             'quantity': 43234,
            ...             'categories': [
            ...                 {
            ...                     'name': 'person.person',
            ...                     'quantity': 43234
            ...                 }
            ...             ]
            ...         }
            ...     }
            ... )
            >>> label_statistics.dumps()
            ... {
            ...    'BOX3D': {
            ...        'quantity': 1234
            ...     },
            ...    'KEYPOINTS2D': {
            ...         'quantity': 43234,
            ...         'categories': [
            ...             {
            ...                 'name': 'person.person',
            ...                 'quantity': 43234
            ...             }
            ...         ]
            ...     }
            ... }

        """
        return self._data
