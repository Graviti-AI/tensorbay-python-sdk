#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Frame.

:class:`Frame` is a concept in :class:`~graviti.dataset.dataset.FusionDataset`.

It is the structure that composes a :class:`~graviti.dataset.segment.FusionSegment`,
and consists of multiple :class:`~graviti.dataset.data.Data` collected at the same time
from different sensors.

"""

from typing import Any, Dict, Iterable, Optional, Type, TypeVar

from ..geometry import Quaternion, Transform3D
from ..utility import UserMutableMapping, common_loads
from .data import Data


class Frame(UserMutableMapping[str, Data]):
    """This class defines the concept of frame.

    Frame is a concept in :class:`~graviti.dataset.dataset.FusionDataset`.

    It is the structure that composes :class:`~graviti.dataset.segment.FusionSegment`,
    and consists of multiple :class:`~graviti.dataset.data.Data` collected at the same time
    corresponding to different sensors.

    Since :class:`Frame` extends :class:`~graviti.utility.user.UserMutableMapping`,
    its basic operations are the same as a dict's.

    To initialize a Frame and add a :class:`~graviti.dataset.data.Data` to it:

    .. code:: python

        frame = Frame()
        frame[sensor_name] = Data()

    """

    _T = TypeVar("_T", bound="Frame")

    def __init__(self, index: Optional[float] = None, frame_id: Optional[str] = None) -> None:
        self._data: Dict[str, Data] = {}
        self._pose: Optional[Transform3D] = None
        if index is not None:
            self._index = index
        if frame_id:
            self._frame_id = frame_id

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a :class:`Frame` object from a dict containing the frame information.

        Arguments:
            contents: A dict containing the information of a frame,
                whose format should be like::

                    {
                        "pose": {
                            "translation": {
                                "x":
                                "y":
                                "z":
                            },
                            "rotation": {
                                "w":
                                "x":
                                "y":
                                "z":
                            },
                        },
                        "frame": {
                            <key>: data_dict{...},
                            <key>: data_dict{...},
                            ...
                            ...
                        }
                    }

        Returns:
            The loaded :class:`Frame` object.

        """
        return common_loads(cls, contents)

    def _loads(self, contents: Dict[str, Any]) -> None:
        self._data = {}
        for sensor, data in contents["frame"].items():
            self._data[sensor] = Data.loads(data)
        self._pose = Transform3D.loads(contents["pose"]) if "pose" in contents else None

    def dumps(self) -> Dict[str, Any]:
        """Dumps the current frame into a dict.

        Returns:
            A dict containing all the information of the frame.

        """
        contents: Dict[str, Any] = {}
        if self._pose:
            contents["pose"] = self._pose.dumps()

        frame = {}
        for sensor, data in self._data.items():
            frame[sensor] = data.dumps()
        contents["frame"] = frame

        return contents

    @property
    def pose(self) -> Optional[Transform3D]:
        """Return the pose of the frame.

        Returns:
            A :class:`~graviti.geometry.transform.Transform3D` object
            representing the pose of the frame.

        """
        return self._pose

    def set_pose(
        self,
        transform: Transform3D.TransformType = None,
        *,
        translation: Optional[Iterable[float]] = None,
        rotation: Quaternion.ArgsType = None,
        contents: Optional[Dict[str, Dict[str, float]]] = None,
        **kwargs: Quaternion.KwargsType,
    ) -> None:
        """Set the pose of the current frame.

        Arguments:
            transform: The transform representing the frame pose in
                a :class:`~graviti.geometry.transform.Transform3D` object
                or a 4x4 or 3x4 transformation matrix.
            translation: Translation of the frame pose in a sequence of [x, y, z].
            rotation: Rotation of the frame pose in a sequence of [w, x, y, z]
                or a 3x3 rotation matrix
                or a :class:`~graviti.geometry.quaternion.Quaternion` object.
            contents: A dict containing the translation and the rotation of the frame pose.
            **kwargs: Other parameters to initialize the rotation of the frame pose.
                See :class:`~graviti.geometry.quaternion.Quaternion` documents for details.

        """
        if contents:
            self._pose = Transform3D.loads(contents)
            return

        self._pose = Transform3D(transform, translation=translation, rotation=rotation, **kwargs)
