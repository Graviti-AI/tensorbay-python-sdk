#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of the Free Spoken Digit dataset."""

import os

from ...dataset import Data, Dataset
from ...label import Classification
from .._utility import glob

DATASET_NAME = "Free Spoken Digit"

_METADATA = {
    "jackson": {"gender": "male", "accent": "USA/neutral", "language": "english"},
    "nicolas": {"gender": "male", "accent": "BEL/French", "language": "english"},
    "theo": {"gender": "male", "accent": "USA/neutral", "language": "english"},
    "yweweler": {"gender": "male", "accent": "DEU/German", "language": "english"},
    "george": {"gender": "male", "accent": "GRC/Greek", "language": "english"},
    "lucas": {"gender": "male", "accent": "DEU/German", "language": "english"},
}


def FSDD(path: str) -> Dataset:
    """Dataloader of the Free Spoken Digit dataset.

    Arguments:
        path: The root directory of the dataset.
            The file structure should be like::

                <path>
                    recordings/
                        0_george_0.wav
                        0_george_1.wav
                        ...

    Returns:
        Loaded `Dataset` object.

    """
    label_map = {}
    for key, value in _METADATA.items():
        attributes = {"name": key}
        attributes.update(value)
        label_map[key] = attributes

    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))
    segment = dataset.create_segment()
    audio_paths = glob(os.path.join(path, "recordings", "*.wav"))
    for audio_path in audio_paths:
        category, name = os.path.basename(audio_path).split("_")[:2]
        data = Data(audio_path)
        data.label.classification = Classification(category, label_map[name])
        segment.append(data)
    return dataset
