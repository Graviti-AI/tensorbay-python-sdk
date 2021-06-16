#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import os
from typing import Any, Dict, Tuple

from ...dataset import Data, Dataset
from ...exception import ModuleImportError
from ...label import CategoryInfo, Classification, ClassificationSubcatalog
from ...utility import NameList
from .._utility import glob

DATASET_NAME = "CACD"
_ATTRIBUTES = {
    "attributes": [
        {
            "name": "name",
            "type": "string",
            "description": "celebrity name",
        },
        {
            "name": "age",
            "type": "number",
            "minimum": 14,
            "maximum": 62,
            "description": "Estimated age of the celebrity",
        },
        {
            "name": "birth",
            "type": "number",
            "minimum": 1951,
            "maximum": 1990,
            "description": "Celebrity birth year",
        },
        {
            "name": "range",
            "type": "number",
            "minimum": 1,
            "maximum": 50,
            "description": "Rank of the celebrity with same birth year in IMDB.com",
        },
        {
            "name": "year",
            "type": "number",
            "minimum": 2004,
            "maximum": 2013,
            "description": "Estimated year of which the photo was taken",
        },
        {
            "name": "lfw",
            "type": "boolean",
            "description": "Whether the celebrity is in LFW dataset.",
        },
    ]
}
_MAT_KEYS = ("name", "identity", "age", "birth", "lfw", "rank", "year")


def CACD(path: str) -> Dataset:
    """Dataloader of `Cross-Age Celebrity Dataset (CACD)`_ dataset.

    .. _Cross-Age Celebrity Dataset (CACD): https://bcsiriuschen.github.io/CARC/

    The file structure should be like::

        <path>
            CACD2000/
                14_Aaron_Johnson_0001.jpg
                ...
            celebrity2000.mat

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset(DATASET_NAME)
    dataset.catalog.classification = _get_subcatalog()
    segment = dataset.create_segment()
    image_files = glob(os.path.join(root_path, "CACD2000", "*.jpg"))
    labels_map = _get_labels_map(os.path.join(root_path, "celebrity2000.mat"))
    for image in image_files:
        category, attribute = labels_map[os.path.basename(image)]
        image_data = Data(image)
        image_data.label.classification = Classification(category, attribute)
        segment.append(image_data)
    return dataset


def _get_labels_map(path: str) -> Dict[str, Tuple[str, Dict[str, Any]]]:
    """Get celebrity_image_data from .mat file.

    Arguments:
        path: The root directory of the dataset.

    Raises:
        ModuleImportError: When the module "h5py" can not be found.

    Returns:
        A Dict of attributes.

    """
    try:
        from h5py import File  # pylint: disable=import-outside-toplevel
    except ModuleNotFoundError as error:
        raise ModuleImportError(error.name) from error  # type: ignore[arg-type]

    mat_file = File(path, "r")
    celebrity_image_data = mat_file["celebrityImageData"]
    celebrity_data = mat_file["celebrityData"]

    # Name is a h5r object which can be searched in .mat file.
    id2name_map = {
        identity: _hdf5_to_str(mat_file[name])
        for identity, name in zip(celebrity_data["identity"][0], celebrity_data["name"][0])
    }
    labels_map = {}
    # The "name" is not the name of the celebrity but the name of the image file.
    for name, identity, *values in zip(*(celebrity_image_data[key][0] for key in _MAT_KEYS)):
        attribute = {"name": id2name_map[identity]}
        attribute.update(zip(_MAT_KEYS[2:], values))
        labels_map[_hdf5_to_str(mat_file[name])] = (str(int(identity)).zfill(4), attribute)
    return labels_map


def _get_subcatalog() -> ClassificationSubcatalog:
    categories: NameList[CategoryInfo] = NameList()
    for i in range(1, 2001):
        categories.append(CategoryInfo(str(i).zfill(4)))
    classification_subcatalog = ClassificationSubcatalog.loads(_ATTRIBUTES)
    classification_subcatalog.categories = categories
    return classification_subcatalog


def _hdf5_to_str(hdf5_string: Any) -> str:
    return "".join(chr(c[0]) for c in hdf5_string)
