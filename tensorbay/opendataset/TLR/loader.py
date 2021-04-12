#!/usr/bin/env python3
#
# Copytright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import os
from collections import defaultdict
from typing import Dict, List
from xml.dom.minidom import parse

from ...dataset import Data, Dataset
from ...label import LabeledBox2D
from .._utility import glob

DATASET_NAME = "TLR"


def TLR(path: str) -> Dataset:
    """Dataloader of the `TLR`_ dataset.

    .. _TLR: http://www.lara.prd.fr/benchmarks/trafficlightsrecognition

    The file structure should like::

        <path>
            root_path/
                Lara3D_URbanSeq1_JPG/
                    frame_011149.jpg
                    frame_011150.jpg
                    frame_<frame_index>.jpg
                    ...
                Lara_UrbanSeq1_GroundTruth_cvml.xml

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    segment = dataset.create_segment()

    file_paths = glob(os.path.join(root_path, "Lara3D_UrbanSeq1_JPG", "*.jpg"))
    labels = _parse_xml(os.path.join(root_path, "Lara_UrbanSeq1_GroundTruth_cvml.xml"))
    for file_path in file_paths:
        # the image file name looks like:
        # frame_000001.jpg
        frame_index = int(os.path.basename(file_path)[6:-4])
        data = Data(file_path)
        data.label.box2d = labels[frame_index]
        segment.append(data)
    return dataset


def _parse_xml(xml_path: str) -> Dict[int, List[LabeledBox2D]]:
    dom = parse(xml_path)
    frames = dom.documentElement.getElementsByTagName("frame")

    labels = defaultdict(list)

    for frame in frames:
        index = int(frame.getAttribute("number"))
        objects = frame.getElementsByTagName("objectlist")[0]
        for obj in objects.getElementsByTagName("object"):
            box = obj.getElementsByTagName("box")[0]
            box_h = int(box.getAttribute("h"))
            box_w = int(box.getAttribute("w"))
            box_xc = int(box.getAttribute("xc"))
            box_yc = int(box.getAttribute("yc"))

            labels[index].append(
                LabeledBox2D.from_xywh(
                    x=box_xc - box_w // 2,
                    y=box_yc - box_h // 2,
                    width=box_w,
                    height=box_h,
                    category=obj.getElementsByTagName("subtype")[0].firstChild.data,
                )
            )
    return labels
