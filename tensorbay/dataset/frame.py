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
from typing import Any, Dict, Optional, Type, TypeVar
from uuid import UUID

from ulid import ULID, from_str, from_uuid

from ..utility import UserMutableMapping, common_loads
from .data import DataBase

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

    def _loads(self, contents: Dict[str, Any]) -> None:
        self._data = {}
        if "frameId" in contents:
            try:
                self.frame_id = from_str(contents["frameId"])
            except ValueError:
                # Legacy fusion dataset use uuid as frame ID
                # Keep this code here to make SDK compatible with uuid
                self.frame_id = from_uuid(UUID(contents["frameId"]))
                if self.__class__._logger_flag:  # pylint: disable=protected-access
                    self.__class__._logger_flag = False  # pylint: disable=protected-access
                    logger.warning(
                        "WARNING: This is a legacy fusion dataset which use uuid as frame ID, "
                        "it should be updated to ulid."
                    )

        for data_contents in contents["frame"]:
            self._data[data_contents["sensorName"]] = DataBase.loads(data_contents)

        # self._pose = Transform3D.loads(contents["pose"]) if "pose" in contents else None

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a :class:`Frame` object from a dict containing the frame information.

        Arguments:
            contents: A dict containing the information of a frame,
                whose format should be like::

                    {
                        "frameId": <str>,
                        "frame": [
                            {
                                "sensorName": <str>,
                                "remotePath" or "localPath": <str>,
                                "timestamp": <float>,
                                "label": {...}
                            },
                            ...
                            ...
                        ]
                    }

        Returns:
            The loaded :class:`Frame` object.

        """
        return common_loads(cls, contents)

    # @property
    # def pose(self) -> Optional[Transform3D]:
    #     """Return the pose of the frame.

    #     Returns:
    #         A :class:`~tensorbay.geometry.transform.Transform3D` object
    #         representing the pose of the frame.

    #     """
    #     return self._pose

    def dumps(self) -> Dict[str, Any]:
        """Dumps the current frame into a dict.

        Returns:
            A dict containing all the information of the frame.

        """
        contents: Dict[str, Any] = {}
        # if self._pose:
        #     contents["pose"] = self._pose.dumps()
        if hasattr(self, "frame_id"):
            contents["frameId"] = str(self.frame_id)

        frame = []
        for sensor_name, data in self._data.items():
            data_contents = {"sensorName": sensor_name}
            data_contents.update(data.dumps())
            frame.append(data_contents)

        contents["frame"] = frame

        return contents

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
