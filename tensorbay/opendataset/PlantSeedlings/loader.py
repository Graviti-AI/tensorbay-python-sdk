#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import os
from typing import Dict, Iterator

import numpy as np

from ...dataset import Data, Dataset, Segment
from ...label import Classification, SemanticMask
from .._utility import glob

try:
    from PIL import Image
except ModuleNotFoundError:
    from .._utility.mocker import Image

_FULLIMAGES_MAP = {
    (1, 4): "Maize",
    (5, 8): "Common wheat",
    (9, 12): "Sugar beet",
    (13, 16): "scentless mayweed",
    (17, 20): "Common Chickweed",
    (21, 24): "shepherd's-purse",
    (25, 28): "Cleavers",
    (29, 32): "Fersken pileurt",
    (33, 36): "Charlock",
    (37, 40): "Fat Hen",
    (41, 44): "Cranes-bill",
    (45, 48): "Field Pansy",
    (49, 52): "Black grass",
    (53, 56): "Loose Silky-bent",
}

_SKIP_FOLDERS = {"Segmented", "Fullimages", "single_channel_segmented"}


def PlantSeedlings(path: str) -> Dataset:
    """Dataloader of PlantSeedlings dataset.

    .. PlantSeedlings: https://vision.eng.au.dk/plant-seedlings-dataset/

    The file structure should be like::

        <path>
            Black-grass/
                1.png
                2.png
                ...
            Charlock/
            Cleavers/
            Common Chickweed/
            Common wheat/
            Fat Hen/
            Loose Silky-bent/
            Maize/
            Scentless Mayweed/
            Shepherd’s Purse/
            Small-flowered Cranesbill/
            Sugar beet/
            Segmented/
                Black-grass/
                 1.png
                 2.png
                 ...
                Charlock/
                Cleavers/
                Common Chickweed/
                Common wheat/
                Fat Hen/
                Loose Silky-bent/
                Maize/
                Scentless Mayweed/
                Shepherd’s Purse/
                Small-flowered Cranesbill/
                Sugar beet/


    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset("PlantSeedlings")
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    category_id_map = dataset.catalog.semantic_mask.get_category_to_index()
    for subset in os.listdir(root_path):
        if subset in _SKIP_FOLDERS:
            continue
        dataset.add_segment(_get_segment(root_path, subset, category_id_map))
    return dataset


def PlantSeedlingsFullimages(path: str) -> Dataset:
    """Dataloader of PlantSeedlings_Fullimages dataset.

    .. PlantSeedlings: https://vision.eng.au.dk/plant-seedlings-dataset/

    The file structure should be like::

        <path>
            Fullimages/
                1/
                    IMG_0573_12-03.png
                    ...
                2/
                    ...
                ...
                SpeciesIndex.pdf
                SpeciesIndex.xlsx

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset("PlantSeedlings_Fullimages")
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog_Fullimages.json"))
    dataset.add_segment(_get_fullimages_segment(root_path))
    return dataset


def _get_fullimages_segment(root_path: str) -> Segment:
    segment = Segment("Fullimages")
    files_path = os.path.join(root_path, "Fullimages")
    category_map = _get_category_map()
    for file_path in glob(os.path.join(files_path, "[0-9]*")):
        segment.extend(
            _generate_fullimages_data(file_path, category_map[os.path.basename(file_path)])
        )
    return segment


def _get_category_map() -> Dict[str, str]:
    category_map = {}
    for key, value in _FULLIMAGES_MAP.items():
        for index in range(key[0], key[1] + 1):
            category_map[str(index)] = value
    return category_map


def _generate_fullimages_data(data_path: str, category: str) -> Iterator[Data]:
    folder_name = os.path.basename(data_path)
    for data_sub_path in os.listdir(data_path):
        data = Data(
            os.path.join(data_path, data_sub_path),
            target_remote_path=f"{folder_name.zfill(2)}/{data_sub_path}",
        )
        data.label.classification = Classification(category=category)
        yield data


def _get_segment(root_path: str, subset: str, category_id_map: Dict[str, int]) -> Segment:
    category_id = category_id_map[subset]
    segment = Segment(subset.replace(" ", "_"))
    data_path = os.path.join(root_path, subset)
    segmented_path = os.path.join(root_path, "Segmented", subset)
    single_channel_segmented_path = os.path.join(root_path, "single_channel_segmented", subset)
    os.makedirs(single_channel_segmented_path, exist_ok=True)
    segment.extend(
        _generate_data(data_path, segmented_path, single_channel_segmented_path, category_id)
    )
    return segment


def _generate_data(
    data_path: str, segmented_path: str, single_channel_segmented_path: str, category_id: int
) -> Iterator[Data]:
    for image_filename in os.listdir(data_path):
        semantic_mask_path = os.path.join(segmented_path, image_filename)
        if not os.path.exists(semantic_mask_path):
            # Discard data without mask
            continue
        data = Data(
            os.path.join(data_path, image_filename),
            target_remote_path=image_filename.zfill(7),
        )
        semantic_mask = _get_semantic_mask(
            semantic_mask_path, image_filename, single_channel_segmented_path, category_id
        )
        data.label.semantic_mask = SemanticMask(semantic_mask)
        yield data


def _get_semantic_mask(
    semantic_mask_path: str,
    image_filename: str,
    single_channel_segmented_path: str,
    category_id: int,
) -> str:
    mask_filename = os.path.join(single_channel_segmented_path, image_filename)
    if os.path.exists(mask_filename):
        return mask_filename
    mask = np.array(Image.open(semantic_mask_path)).sum(axis=2)
    mask[mask > 0] = category_id
    Image.fromarray(np.uint8(mask)).save(mask_filename)
    return mask_filename
