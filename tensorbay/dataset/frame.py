#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Frame.

:class:`Frame` is a concept in :class:`~tensorbay.dataset.dataset.FusionDataset`.

It is the structure that composes a :class:`~tensorbay.dataset.segment.FusionSegment`,
and consists of multiple :class:`~tensorbay.dataset.data.Data` collected at the same time
from different sensors.

"""

import logging
from typing import Any, Dict, Mapping, Optional, Sequence, Type, TypeVar
from uuid import UUID

from ulid import ULID, from_str, from_uuid

from ..utility import UserMutableMapping
from .data import DataBase, RemoteData

logger = logging.getLogger(__name__)


class Frame(UserMutableMapping[str, "DataBase._Type"]):
    """This class defines the concept of frame.

    Frame is a concept in :class:`~tensorbay.dataset.dataset.FusionDataset`.

    It is the structure that composes :class:`~tensorbay.dataset.segment.FusionSegment`,
    and consists of multiple :class:`~tensorbay.dataset.data.Data` collected at the same time
    corresponding to different sensors.

    Since :class:`Frame` extends :class:`~tensorbay.utility.user.UserMutableMapping`,
    its basic operations are the same as a dictionary's.

    To initialize a Frame and add a :class:`~tensorbay.dataset.data.Data` to it:

    .. code:: python

        frame = Frame()
        frame[sensor_name] = Data()

    """

    _T = TypeVar("_T", bound="Frame")
    _logger_flag = True

    def __init__(self, frame_id: Optional[ULID] = None) -> None:
        self._data: Dict[str, DataBase._Type] = {}
        # self._pose: Optional[Transform3D] = None
        if frame_id:
            self.frame_id = frame_id

    def _repr_head(self) -> str:
        if hasattr(self, "frame_id"):
            return f'{self.__class__.__name__}("{self.frame_id}")'

        return self.__class__.__name__

    @classmethod
    def from_response_body(
        cls: Type[_T], body: Dict[str, Any], frame_index: int, urls: Sequence[Mapping[str, str]]
    ) -> _T:
        """Loads a :class:`Frame` object from a response body.

        Arguments:
            body: The response body which contains the information of a frame,
                whose format should be like::

                    {
                        "frameId": <str>,
                        "frame": [
                            {
                                "sensorName": <str>,
                                "remotePath": <str>,
                                "timestamp": <float>,
                                "label": {...}
                            },
                            ...
                            ...
                        ]
                    }

            frame_index: The index of the frame.
            urls: A sequence of mappings which key is the sensor name and value is the url.

        Returns:
            The loaded :class:`Frame` object.

        """  # noqa: DAR101  # https://github.com/terrencepreilly/darglint/issues/120
        try:
            frame_id = from_str(body["frameId"])
        except ValueError:
            # Legacy fusion dataset use uuid as frame ID
            # Keep this code here to make SDK compatible with uuid
            frame_id = from_uuid(UUID(body["frameId"]))
            if cls._logger_flag:  # pylint: disable=protected-access
                cls._logger_flag = False  # pylint: disable=protected-access
                logger.warning(
                    "WARNING: This is a legacy fusion dataset which use uuid as frame ID, "
                    "it should be updated to ulid."
                )
        frame = cls(frame_id)
        for data_contents in body["frame"]:
            sensor_name = data_contents["sensorName"]
            frame[sensor_name] = RemoteData.from_response_body(
                data_contents,
                _url_getter=lambda _, s=sensor_name: urls[frame_index][s],  # type: ignore[misc]
            )

        return frame

    # @property
    # def pose(self) -> Optional[Transform3D]:
    #     """Return the pose of the frame.

    #     Returns:
    #         A :class:`~tensorbay.geometry.transform.Transform3D` object
    #         representing the pose of the frame.

    #     """
    #     return self._pose

    # def set_pose(
    #     self,
    #     translation: Optional[Iterable[float]] = (0, 0, 0),
    #     rotation: Transform3D.RotationType = (1, 0, 0, 0),
    #     *,
    #     matrix: Optional[MatrixType] = None,
    # ) -> None:
    #     """Set the pose of the current frame.

    #     Arguments:
    #         translation: Translation of the frame pose in a sequence of [x, y, z].
    #         rotation: Rotation of the frame pose in a sequence of [w, x, y, z]
    #             or a numpy quaternion object.
    #         matrix: The transform representing the frame pose in
    #             a 4x4 or 3x4 transform matrix.

    #     """
    #     self._pose = Transform3D(translation, rotation, matrix=matrix)
