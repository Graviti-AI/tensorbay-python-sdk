#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name
# pylint: disable=missing-module-docstring

import os

from ...dataset import Data, Dataset
from ...label import Classification
from .._utility import glob

DATASET_NAME = "Newsgroups20"
SEGMENT_DESCRIPTION_DICT = {
    "20_newsgroups": "Original 20 Newsgroups data set",
    "20news-bydate-train": (
        "Training set of the second version of 20 Newsgroups, "
        "which is sorted by date and has duplicates and some headers removed"
    ),
    "20news-bydate-test": (
        "Test set of the second version of 20 Newsgroups, "
        "which is sorted by date and has duplicates and some headers removed"
    ),
    "20news-18828": (
        "The third version of 20 Newsgroups, which has duplicates removed "
        "and includes only 'From' and 'Subject' headers"
    ),
}


def Newsgroups20(path: str) -> Dataset:
    """Dataloader of the `20 Newsgroups`_ dataset.

    .. _20 Newsgroups: http://qwone.com/~jason/20Newsgroups/

    The folder structure should be like::

        <path>
            20news-18828/
                alt.atheism/
                    49960
                    51060
                    51119
                    51120
                    ...
                comp.graphics/
                comp.os.ms-windows.misc/
                comp.sys.ibm.pc.hardware/
                comp.sys.mac.hardware/
                comp.windows.x/
                misc.forsale/
                rec.autos/
                rec.motorcycles/
                rec.sport.baseball/
                rec.sport.hockey/
                sci.crypt/
                sci.electronics/
                sci.med/
                sci.space/
                soc.religion.christian/
                talk.politics.guns/
                talk.politics.mideast/
                talk.politics.misc/
                talk.religion.misc/
            20news-bydate-test/
            20news-bydate-train/
            20_newsgroups/

    Arguments:
        path: The root directory of the dataset.

    Returns:
        Loaded :class:`~tensorbay.dataset.dataset.Dataset` instance.

    """
    root_path = os.path.abspath(os.path.expanduser(path))
    dataset = Dataset(DATASET_NAME)
    dataset.load_catalog(os.path.join(os.path.dirname(__file__), "catalog.json"))

    for segment_name, segment_description in SEGMENT_DESCRIPTION_DICT.items():
        segment_path = os.path.join(root_path, segment_name)
        if not os.path.isdir(segment_path):
            continue

        segment = dataset.create_segment(segment_name)
        segment.description = segment_description

        text_paths = glob(os.path.join(segment_path, "*", "*"))
        for text_path in text_paths:
            category = os.path.basename(os.path.dirname(text_path))

            data = Data(
                text_path, target_remote_path=f"{category}/{os.path.basename(text_path)}.txt"
            )
            data.label.classification = Classification(category)
            segment.append(data)

    return dataset
