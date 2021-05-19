#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""TensorBay Resource Name (TBRN) related classes.

:class:`TBRNType` is an enumeration type, which has 7 types: 'DATASET', 'SEGMENT', 'FRAME',
'SEGMENT_SENSOR', 'FRAME_SENSOR', 'NORMAL_FILE' and 'FUSION_FILE'.

:class:`TBRN` is a TensorBay Resource Name(TBRN) parser and generator.

"""

from enum import Enum, Flag, auto
from typing import Any, List, Optional, Tuple, TypeVar

from ..exception import TBRNError


class _TBRNFlag(Flag):
    FIELD_HEAD = 1 << 0
    FIELD_DATASET = 1 << 1
    FIELD_SEGMENT = 1 << 2
    FIELD_FRAME = 1 << 3
    FIELD_SENSOR = 1 << 4
    FIELD_PATH = 1 << 5

    # tb:[dataset]
    DATASET = FIELD_HEAD | FIELD_DATASET

    # tb:[dataset]:[segment]
    SEGMENT = FIELD_HEAD | FIELD_DATASET | FIELD_SEGMENT

    # tb:[dataset]:[segment]:[frame]
    FRAME = FIELD_HEAD | FIELD_DATASET | FIELD_SEGMENT | FIELD_FRAME

    # tb:[dataset]:[segment]::[sensor]
    SEGMENT_SENSOR = FIELD_HEAD | FIELD_DATASET | FIELD_SEGMENT | FIELD_SENSOR

    # tb:[dataset]:[segment]:[frame]:[sensor]
    FRAME_SENSOR = FIELD_HEAD | FIELD_DATASET | FIELD_SEGMENT | FIELD_FRAME | FIELD_SENSOR

    # tb:[dataset]:[segment]://[remote_path]
    NORMAL_FILE = FIELD_HEAD | FIELD_DATASET | FIELD_SEGMENT | FIELD_PATH

    # tb:[dataset]:[segment]:[frame]:[sensor]://[remote_path]
    FUSION_FILE = (
        FIELD_HEAD | FIELD_DATASET | FIELD_SEGMENT | FIELD_FRAME | FIELD_SENSOR | FIELD_PATH
    )


class TBRNType(Enum):
    """TBRNType defines the type of a TBRN.

    It has 7 types:

        1. `TBRNType.DATASET`::

            "tb:VOC2012"

        which means the dataset "VOC2012".

        2. `TBRNType.SEGMENT`::

            "tb:VOC2010:train"

        which means the "train" segment of dataset "VOC2012".

        3. `TBRNType.FRAME`::

            "tb:KITTI:test:10"

        which means the 10th frame of the "test" segment in dataset "KITTI".

        4. `TBRNType.SEGMENT_SENSOR`::

            "tb:KITTI:test::lidar"

        which means the sensor "lidar" of the "test" segment in dataset "KITTI".

        5. `TBRNType.FRAME_SENSOR`::

            "tb:KITTI:test:10:lidar"

        which means the sensor "lidar" which belongs to the 10th frame of the "test" segment in
        dataset "KITTI".

        6. `TBRNType.NORMAL_FILE`::

            "tb:VOC2012:train://2012_004330.jpg"

        which means the file "2012_004330.jpg" of the "train" segment in normal dataset "VOC2012".

        7. `TBRNType.FUSION_FILE`::

            "tb:KITTI:test:10:lidar://000024.bin"

        which means the file "000024.bin" in fusion dataset "KITTI", its segment, frame index and
        sensor is "test", 10 and "lidar".

    """

    DATASET = auto()
    SEGMENT = auto()
    FRAME = auto()
    SEGMENT_SENSOR = auto()
    FRAME_SENSOR = auto()
    NORMAL_FILE = auto()
    FUSION_FILE = auto()


_T = TypeVar("_T")


class TBRN:
    """TBRN is a TensorBay Resource Name(TBRN) parser and generator.

    Use as a generator:

        >>> info = TBRN("VOC2010", "train", remote_path="2012_004330.jpg")
        >>> info.type
        <TBRNType.NORMAL_FILE: 5>
        >>> info.get_tbrn()
        'tb:VOC2010:train://2012_004330.jpg'
        >>> print(info)
        'tb:VOC2010:train://2012_004330.jpg'

    Use as a parser:

        >>> tbrn = "tb:VOC2010:train://2012_004330.jpg"
        >>> info = TBRN(tbrn=tbrn)
        >>> info.dataset
        'VOC2010'
        >>> info.segment_name
        'train'
        >>> info.remote_path
        '2012_004330.jpg'

    Arguments:
        dataset_name: Name of the dataset.
        segment_name: Name of the segment.
        frame_index: Index of the frame.
        sensor_name: Name of the sensor.
        remote_path: Object path of the file.
        tbrn: Full TBRN string.
        draft_number: The draft number (if the status is draft).
        revision: The commit revision (if the status is commit).

    Attributes:
        dataset_name: Name of the dataset.
        segment_name: Name of the segment.
        frame_index: Index of the frame.
        sensor_name: Name of the sensor.
        remote_path: Object path of the file.
        type: The type of this TBRN.
        draft_number: The draft number (if the status is draft).
        revision: The revision (if the status is not draft).
        is_draft: whether the status is draft, True for draft, False for commit.

    Raises:
        TBRNError: The TBRN is invalid.

    """

    _HEAD = "tb"
    _NAMES_SEPARATOR = ":"

    _DRAFT_SEPARATOR = "#"
    _REVISION_SEPARATOR = "@"

    _NAMES_MAX_SPLIT = 4
    _PATH_SEPARATOR = "://"
    _PATH_MAX_SPLIT = 1
    _FRAME_INDEX = 3

    _FLAG_TO_TYPE = {
        _TBRNFlag.DATASET: (TBRNType.DATASET, 1),
        _TBRNFlag.SEGMENT: (TBRNType.SEGMENT, 2),
        # _TBRNFlag.FRAME: (TBRNType.FRAME, 3),
        # _TBRNFlag.SEGMENT_SENSOR: (TBRNType.SEGMENT_SENSOR, 4),
        # _TBRNFlag.FRAME_SENSOR: (TBRNType.FRAME_SENSOR, 4),
        _TBRNFlag.NORMAL_FILE: (TBRNType.NORMAL_FILE, 2),
        # _TBRNFlag.FUSION_FILE: (TBRNType.FUSION_FILE, 4),
    }

    _names: Tuple[
        Optional[str],
        Optional[str],
        Optional[int],
        Optional[str],
        Optional[str],
    ]

    def __init__(  # pylint: disable=too-many-locals
        self,
        dataset_name: Optional[str] = None,
        segment_name: Optional[str] = None,
        frame_index: Optional[int] = None,
        sensor_name: Optional[str] = None,
        *,
        remote_path: Optional[str] = None,
        draft_number: Optional[int] = None,
        revision: Optional[str] = None,
        tbrn: Optional[str] = None,
    ) -> None:
        if tbrn is not None:
            splits = tbrn.split(TBRN._PATH_SEPARATOR, TBRN._PATH_MAX_SPLIT)
            names: List[Any] = splits[0].split(TBRN._NAMES_SEPARATOR, TBRN._NAMES_MAX_SPLIT)

            if names[0] != TBRN._HEAD:
                raise TBRNError('TensorBay Resource Name should startwith "tb:"')

            dataset_name = names[1]
            if not dataset_name:
                raise TBRNError(
                    'TensorBay Resource Name should add dataset name "tb:<dataset name>"'
                )

            self.revision: Optional[str] = None
            self.draft_number: Optional[int] = None

            if TBRN._REVISION_SEPARATOR in dataset_name:
                names[1], self.revision = dataset_name.split(TBRN._REVISION_SEPARATOR, 1)

            elif TBRN._DRAFT_SEPARATOR in dataset_name:
                names[1], number = dataset_name.split(TBRN._DRAFT_SEPARATOR)
                self.draft_number = int(number)
            else:
                names[1] = dataset_name

            names += [None] * (TBRN._NAMES_MAX_SPLIT + 1 - len(names))

            frame_index = names[TBRN._FRAME_INDEX]
            names[TBRN._FRAME_INDEX] = int(frame_index) if frame_index else None

            if len(splits) == TBRN._PATH_MAX_SPLIT + 1:
                names.append(splits[1])
            else:
                names.append(None)

            self._names = tuple(names[1:])  # type: ignore[assignment]

        else:
            self._names = (
                dataset_name,
                segment_name,
                frame_index,
                sensor_name,
                remote_path,
            )

            if draft_number is not None and revision is not None:
                raise TBRNError("TensorBay Resource Name should not contain draft and commit info")

            self.draft_number = draft_number
            self.revision = revision

        try:
            self._type, self._field_length = self._check_type()
        except KeyError as error:
            raise TBRNError("Invalid TensorBay Resource Name") from error

    def __repr__(self) -> str:
        return self.get_tbrn()

    def _check_type(self) -> Tuple[TBRNType, int]:
        # https://github.com/PyCQA/pylint/issues/2224
        flag = _TBRNFlag.FIELD_HEAD.value  # pylint: disable=no-member
        for i, name in enumerate(self._names, 1):
            if name is not None:
                flag |= 1 << i

        return TBRN._FLAG_TO_TYPE[_TBRNFlag(flag)]

    def _raise_when_none(self, value: Optional[_T], field: str) -> _T:
        if value is None:
            raise ValueError(f"TBRNType: '{self.type.name}' has no property '{field}'")
        return value

    @property
    def dataset_name(self) -> str:
        """Return the dataset name.

        Returns:
            The dataset name.

        """
        return self._names[0]  # type: ignore[return-value]

    @property
    def segment_name(self) -> str:
        """Return the segment name.

        Returns:
            The segment name.

        """
        return self._raise_when_none(self._names[1], "segment_name")

    @property
    def frame_index(self) -> int:
        """Return the frame index.

        Returns:
            The frame index.

        """
        return self._raise_when_none(self._names[2], "frame_index")

    @property
    def sensor_name(self) -> str:
        """Return the sensor name.

        Returns:
            The sensor name.

        """
        return self._raise_when_none(self._names[3], "sensor_name")

    @property
    def remote_path(self) -> str:
        """Return the object path.

        Returns:
            The object path.

        """
        return self._raise_when_none(self._names[4], "remote_path")

    @property
    def type(self) -> TBRNType:
        """Return the type of this TBRN.

        Returns:
            The type of this TBRN.

        """
        return self._type

    @property
    def is_draft(self) -> bool:
        """Return the frame index.

        Returns:
            The frame index.

        """
        return bool(self.draft_number)

    def get_tbrn(self, frame_width: int = 0) -> str:
        """Generate the full TBRN string.

        Arguments:
            frame_width: Add '0' at the beginning of the frame_index,
                until it reaches the frame_width.

        Returns:
            The full TBRN string.

        """
        names: List[Any] = [TBRN._HEAD]
        names.extend(self._names[: self._field_length])
        if self._field_length >= TBRN._FRAME_INDEX:
            frame_index = names[TBRN._FRAME_INDEX]
            if frame_index is not None:
                if frame_width:
                    names[TBRN._FRAME_INDEX] = f"{frame_index:0{frame_width}}"
                else:
                    names[TBRN._FRAME_INDEX] = f"{frame_index}"
            else:
                names[TBRN._FRAME_INDEX] = ""
        if self.is_draft:
            names[1] = f"{names[1]}{TBRN._DRAFT_SEPARATOR}{self.draft_number}"
        elif self.revision is not None:
            names[1] = f"{names[1]}{TBRN._REVISION_SEPARATOR}{self.revision}"
        tbrn = TBRN._NAMES_SEPARATOR.join(names)
        if self._names[4] is not None:
            tbrn = f"{tbrn}{TBRN._PATH_SEPARATOR}{self.remote_path}"
        return tbrn
