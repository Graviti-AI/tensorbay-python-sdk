#!/usr/bin/env python3
#
# Copytright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of SegTrack2 dataset."""

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

DATASET_NAME = "SegTrack2"

_SEGMENTS_INFO = {
    1: ("bird_of_paradise", "birdfall", "frog", "girl", "monkey", "parachute", "soldier", "worm"),
    2: ("bmx", "cheetah", "drift", "hummingbird", "monkeydog"),
    6: ("penguin",),
}
_FILENAME_REFORMATTERS = (
    lambda filename: filename,
    lambda filename: f"{os.path.splitext(filename)[0]}.png",
)
_MASK_GETTER = Callable[[str, str, str, int, Callable[[str], str]], InstanceMask]


def SegTrack2(path: str) -> Dataset:
    """`SegTrack2 <https://web.engr.oregonstate.edu/~lif/SegTrack2/dataset.html>`_ dataset.

    The file structure of SegTrack looks like::

        <path>
            GroundTruth/
                bird_of_paradise/
                    bird_of_paradise_00000.png
                    ...
                bmx/
                    1/
                        bmx_06668.png
                        ...
                    2/
                        bmx_06668.png
                        ...
                ...
            JPEGImages/
                bird_of_paradise/
                    bird_of_paradise_00000.png
                    ...
                ...

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.join(os.path.abspath(os.path.expanduser(path)))
    image_dir = os.path.join(root_path, "JPEGImages")
    original_mask_dir = os.path.join(root_path, "GroundTruth")
    mask_dir = os.path.join(root_path, "Masks")
    dataset = Dataset(DATASET_NAME)
    dataset.notes.is_continuous = True
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    for instance_num, segment_names in _SEGMENTS_INFO.items():
        for segment_name in segment_names:
            segment = dataset.create_segment(segment_name)
            mask_subdir = os.path.join(mask_dir, segment_name)
            os.makedirs(mask_subdir, exist_ok=True)
            all_mask_subdirs = {
                "original_mask_subdir": os.path.join(original_mask_dir, segment_name),
                "mask_subdir": mask_subdir,
            }

            filename_reformatter = (
                _FILENAME_REFORMATTERS[1]
                if segment_name in {"penguin", "monkeydog"}
                else _FILENAME_REFORMATTERS[0]
            )
            mask_getter: _MASK_GETTER = (
                _get_cheetah_instance_mask if segment_name == "cheetah" else _get_instance_mask
            )
            for image_path in glob(os.path.join(image_dir, segment_name, "*")):
                segment.append(
                    _get_data(
                        image_path,
                        all_mask_subdirs,
                        instance_num,
                        filename_reformatter,
                        mask_getter,
                    )
                )
    return dataset


def _get_data(
    image_path: str,
    all_mask_subdirs: Dict[str, str],
    instance_num: int,
    filename_reformatter: Callable[[str], str],
    mask_getter: _MASK_GETTER,
) -> Data:
    data = Data(image_path)
    data.label.instance_mask = mask_getter(
        image_path,
        all_mask_subdirs["mask_subdir"],
        all_mask_subdirs["original_mask_subdir"],
        instance_num,
        filename_reformatter,
    )
    return data


def _get_instance_mask(
    image_path: str,
    mask_subdir: str,
    original_mask_subdir: str,
    instance_num: int,
    filename_reformatter: Callable[[str], str],
) -> InstanceMask:
    filename = filename_reformatter(os.path.basename(image_path))
    mask_path = os.path.join(mask_subdir, f"{os.path.splitext(filename)[0]}.png")
    if instance_num == 1:
        mask = _get_reformatted_mask(os.path.join(original_mask_subdir, filename))
    else:
        mask = _get_reformatted_mask(os.path.join(original_mask_subdir, "1", filename))
        for instance_id in range(2, instance_num + 1):
            alter_mask = np.array(
                Image.open(os.path.join(original_mask_subdir, str(instance_id), filename)),
            )[:, :, 0]
            mask[alter_mask == 255] = instance_id

    Image.fromarray(mask).save(mask_path)
    return InstanceMask(mask_path)


def _get_cheetah_instance_mask(
    image_path: str, mask_subdir: str, original_mask_subdir: str, _: int, __: Callable[[str], str]
) -> InstanceMask:
    filename = os.path.basename(image_path)
    new_filename = f"{os.path.splitext(filename)[0]}.png"
    mask_path = os.path.join(mask_subdir, new_filename)
    mask = _get_reformatted_mask(os.path.join(original_mask_subdir, "1", filename))
    alter_mask = np.array(
        Image.open(os.path.join(original_mask_subdir, "2", new_filename)),
    )[:, :, 0]
    mask[alter_mask == 255] = 2

    Image.fromarray(mask).save(mask_path)
    return InstanceMask(mask_path)


def _get_reformatted_mask(original_mask_path: str) -> np.ndarray:
    mask = np.array(Image.open(original_mask_path))[:, :, 0]
    # reformat mask
    # from {background: 0, overlap: 1~254, target: 255}
    # to {background: 0, target: 1, overlap: 255}
    overlap = np.logical_and(mask > 0, mask < 255)
    mask[mask == 255] = 1
    mask[overlap] = 255
    return mask
