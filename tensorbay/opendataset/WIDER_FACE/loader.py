#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import os
from collections import OrderedDict
from itertools import islice
from typing import Dict, Iterator, List, Union

from ...dataset import Data, Dataset
from ...label import Classification, LabeledBox2D

DATASET_NAME = "WIDER_FACE"
_SEGMENT_LIST = {
    "test": "wider_face_test_filelist.txt",
    "train": "wider_face_train_bbx_gt.txt",
    "val": "wider_face_val_bbx_gt.txt",
}
_ATTRIBUTE_MAP_TYPE = Dict[str, List[Union[bool, str]]]


def WIDER_FACE(path: str) -> Dataset:
    """Dataloader of the `WIDER FACE`_ dataset.

    .. _WIDER FACE: http://shuoyang1213.me/WIDERFACE/

    The file structure should be like::

        <path>
            WIDER_train/
                images/
                    0--Parade/
                        0_Parade_marchingband_1_100.jpg
                        0_Parade_marchingband_1_1015.jpg
                        0_Parade_marchingband_1_1030.jpg
                        ...
                    1--Handshaking/
                    ...
                    59--people--driving--car/
                    61--Street_Battle/
            WIDER_val/
                ...
            WIDER_test/
                ...
            wider_face_split/
                wider_face_train_bbx_gt.txt
                wider_face_val_bbx_gt.txt

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    attribute_map = _get_attribute_map(dataset)
    for segment_name, label_file in _SEGMENT_LIST.items():
        segment = dataset.create_segment(segment_name)
        for data in _load_data(
            os.path.join(path, "wider_face_split", label_file), attribute_map, segment_name
        ):
            segment.append(data)
        segment.sort()
    return dataset


def _get_attribute_map(dataset: Dataset) -> _ATTRIBUTE_MAP_TYPE:
    attribute_map: _ATTRIBUTE_MAP_TYPE = OrderedDict()
    for info in dataset.catalog.box2d.attributes:
        if getattr(info, "type", None) == "boolean":
            attribute_map[info.name] = [False, True]
        else:
            attribute_map[info.name] = info.enum  # type: ignore[assignment]
    return attribute_map


def _load_data(path: str, attribute_map: _ATTRIBUTE_MAP_TYPE, segment_name: str) -> Iterator[Data]:
    """Loads the box2d and classification label in to data.

    The train and val label file context should be like::

        0--Parade/0_Parade_marchingband_1_849.jpg
        1
        449 330 122 149 0 0 0 0 0 0
        0--Parade/0_Parade_Parade_0_452.jpg
        0
        0 0 0 0 0 0 0 0 0 0
        0--Parade/0_Parade_marchingband_1_799.jpg
        21
        78 221 7 8 2 0 0 0 0 0
        78 238 14 17 2 0 0 0 0 0
        113 212 11 15 2 0 0 0 0 0
        134 260 15 15 2 0 0 0 0 0

    Arguments:
        path: The path of label file.
        attribute_map: A attribute value enum table.
        segment_name: Name of the segment.

    Yields:
        Data with loaded lables.

    """
    is_test = segment_name == "test"
    with open(path, encoding="utf-8") as fp:
        for image_path in fp:
            event, file_name = image_path.split("/")
            # translate directory name to category. like 0--Parade -> Parade
            category = "_".join(event.split("--")[1:])
            root_path = path.rsplit(os.sep, 2)[0]
            data = Data(
                os.path.join(root_path, f"WIDER_{segment_name}", "images", event, file_name)
            )
            data.label.classification = Classification(category)
            if not is_test:
                label_num = int(fp.readline())

                # when the label num is 0, a line of "0 0 0 0 0 0 0 0 0 0" also given
                if label_num == 0:
                    fp.readline()
                data.label.box2d = []
                for line in islice(fp, label_num):
                    labels = line.strip().split()
                    attributes = {
                        key: mapping[int(value)]
                        for (key, mapping), value in zip(attribute_map.items(), labels[4:10])
                    }
                    data.label.box2d.append(
                        LabeledBox2D.from_xywh(
                            x=int(labels[0]),
                            y=int(labels[1]),
                            width=int(labels[2]),
                            height=int(labels[3]),
                            attributes=attributes,
                        )
                    )

            yield data
