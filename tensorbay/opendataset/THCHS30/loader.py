#!/usr/bin/env python3
#
# Copyright 2021 Graviti. All Rights Reserved.
#
# pylint: disable=invalid-name

"""This file define the THCHS-30 Dataloader"""

import os
from itertools import islice
from typing import List

from ...dataset import Data, Dataset
from ...label import LabeledSentence, SentenceSubcatalog, Word
from .._utility import glob

DATASET_NAME = "THCHS-30"
_SEGMENT_NAME_LIST = ("train", "dev", "test")


def THCHS30(path: str) -> Dataset:
    """Load the THCHS-30 Dataset to TensorBay

    :param path: the root directory of the dataset
    The file structure should be like:
    <path>
        lm_word/
            lexicon.txt
        data/
            A11_0.wav.trn
            ...
        dev/
            A11_101.wav
            ...
        train/
        test/
    :return: a loaded dataset
    """
    dataset = Dataset(DATASET_NAME)
    dataset.catalog.sentence = _get_subcatalog(os.path.join(path, "lm_word", "lexicon.txt"))
    for segment_name in _SEGMENT_NAME_LIST:
        segment = dataset.create_segment(segment_name)
        for filename in glob(os.path.join(path, segment_name, "*.wav")):
            data = Data(filename)
            label_file = os.path.join(path, "data", os.path.basename(filename) + ".trn")
            data.labels.sentence = _get_label(label_file)
            segment.append(data)
    return dataset


def _get_label(label_file: str) -> List[LabeledSentence]:
    with open(label_file) as fp:
        labels = ((Word(text=text) for text in texts.split()) for texts in fp)
        return [LabeledSentence(*labels)]


def _get_subcatalog(lexion_path: str) -> SentenceSubcatalog:
    """Load subcatalog by raw lexicon file because the lexicon file so large"""
    subcatalog = SentenceSubcatalog()
    with open(lexion_path) as fp:
        for line in islice(fp, 4, None):
            subcatalog.append_lexicon(line.strip().split())
    return subcatalog
