#!/usr/bin/env python3
#
# Copytright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of SegTrack dataset."""

import os
from typing import Callable, Dict

import numpy as np

from tensorbay.dataset import Data, Dataset
from tensorbay.label import InstanceMask
from tensorbay.opendataset._utility import glob

try:
    from PIL import Image
except ModuleNotFoundError:
    from tensorbay.opendataset._utility.mocker import Image  # pylint:disable=ungrouped-imports

DATASET_NAME = "SegTrack"

_SEGMENTS_INFO: Dict[str, Callable[[str], str]] = {
    "birdfall2": lambda stem: f"{stem}.png",
    "cheetah": lambda stem: f"chasedeer_{str(int(stem[-2:]) - 1).zfill(5)}.png",
    "girl": lambda stem: f"{int(stem[-2:]) - 61}.bmp",
    "monkeydog": lambda stem: f"Comp_00{stem}.png",
    "parachute": lambda stem: f"{stem}.png",
    "penguin": lambda stem: f"{stem}.png",
}


def SegTrack(path: str) -> Dataset:
    """`SegTrack <http://cpl.cc.gatech.edu/projects/SegTrack/>`_ dataset.

    The file structure of SegTrack looks like::

        <path>
            birdfall2/
                birdfall2_00018.png
                ...
                ground-truth/
                    birdfall2_00018.png
                    ...
            cheetah/
                chasedeer_frame_0001.bmp
                ...
                ground-truth/
                    chasedeer_00000.png
                    ...
            girl/
                5117-8_70161.bmp
                ...
                ground-truth/
                    0.bmp
                    ...
            monkeydog/
                195.bmp
                ...
                ground-truth/
                    Comp_00195.png
                    ...
            parachute/
                parachute_00000.png
                ...
                ground-truth/
                    parachute_00000.png
                    ...
            penguin/
                penguin_00000.bmp
                ...
                ground_truth/
                    penguin_00000.png
                    ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.join(os.path.abspath(os.path.expanduser(path)))
    dataset = Dataset(DATASET_NAME)
    dataset.notes.is_continuous = True
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name, filename_reformatter in _SEGMENTS_INFO.items():
        segment = dataset.create_segment(segment_name)
        segment_dir = os.path.join(root_path, segment_name)
        mask_dir = os.path.join(segment_dir, "masks")
        os.makedirs(mask_dir, exist_ok=True)
        mask_name = "ground_truth" if segment_name == "penguin" else "ground-truth"
        original_mask_dir = os.path.join(segment_dir, mask_name)
        for image_path in glob(os.path.join(segment_dir, "*.*")):
            data = Data(image_path)
            data.label.instance_mask = _get_instance_mask(
                image_path, mask_dir, original_mask_dir, filename_reformatter
            )
            segment.append(data)
    return dataset


def _get_instance_mask(
    image_path: str,
    mask_dir: str,
    original_mask_dir: str,
    filename_reformatter: Callable[[str], str],
) -> InstanceMask:
    stem = os.path.splitext(os.path.basename(image_path))[0]
    mask_path = os.path.join(mask_dir, f"{stem}.png")
    mask = np.array(
        Image.open(os.path.join(original_mask_dir, filename_reformatter(stem))),
    )[:, :, 0]
    # reformat mask
    # from {background: 0, overlap: 1~254, target: 255}
    # to {background: 0, target: 1, overlap: 255}
    overlap = np.logical_and(mask > 0, mask < 255)
    mask[mask == 255] = 1
    mask[overlap] = 255
    Image.fromarray(mask).save(mask_path)
    return InstanceMask(mask_path)
