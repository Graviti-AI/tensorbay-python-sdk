#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
"""Generate rst flies in Examples."""

import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3]))
from docs.source._templates import (  # noqa: E402 # pylint: disable=wrong-import-position
    EXAMPLES_TEMPLATE,
)

_DATASET_NAMES = (
    "Dogs Vs Cats",
    "20 Newsgroups",
    "BSTLD",
    "Neolix OD",
    "Leeds Sports Pose",
    "THCHS-30",
)
_LABEL_TYPES = (
    "Classification",
    "Classification",
    "Box2D",
    "Box3D",
    "Keypoints2D",
    "Sentence",
)
_FILE_NAMES = ("DogsVsCats", "Newsgroups20", "BSTLD", "NeolixOD", "LeedsSportsPose", "THCHS30")

_DATASET_WITH_IMAGES = ("BSTLD", "Neolix OD", "Leeds Sports Pose")

_FIGURE_DESCRIPTION = """(:numref:`Fig. %s <example-{file_name}>`).

.. _example-{file_name}:

.. figure:: ../../../images/example-{label_type}.png
   :scale: 50 %
   :align: center

   The preview of a cropped image with labels from "{dataset_name}".
"""

_CATEGORY_ATTRIBUTE_DESCRIPTIONS = {}
_CATEGORY_ATTRIBUTE_DESCRIPTIONS[
    "BSTLD"
] = """
The only annotation type for "{dataset_name}" is
:ref:`reference/label_format/{label_type}:{label_type}`, and there are 13
:ref:`reference/label_format/CommonLabelProperties:category` types and one
:ref:`reference/label_format/CommonLabelProperties:attributes` type.
"""

_CATEGORY_ATTRIBUTE_DESCRIPTIONS[
    "Dogs Vs Cats"
] = """
The only annotation type for "{dataset_name}" is
:ref:`reference/label_format/{label_type}:{label_type}`, and there are 2
:ref:`reference/label_format/CommonLabelProperties:category` types.
"""

_CATEGORY_ATTRIBUTE_DESCRIPTIONS[
    "Leeds Sports Pose"
] = """
The only annotation type for "{dataset_name}" is
:ref:`reference/label_format/{label_type}:{label_type}`.
"""

_CATEGORY_ATTRIBUTE_DESCRIPTIONS[
    "Neolix OD"
] = """
The only annotation type for "{dataset_name}" is
:ref:`reference/label_format/{label_type}:{label_type}`, and there are 15
:ref:`reference/label_format/CommonLabelProperties:category` types and 3
:ref:`reference/label_format/CommonLabelProperties:attributes` type.
"""

_CATEGORY_ATTRIBUTE_DESCRIPTIONS[
    "20 Newsgroups"
] = """
The only annotation type for "{dataset_name}" is
:ref:`reference/label_format/{label_type}:{label_type}`, and there are 20
:ref:`reference/label_format/CommonLabelProperties:category` types
"""

_CATEGORY_ATTRIBUTE_DESCRIPTIONS["THCHS-30"] = ""

_CATALOG_DESCRIPTIONS = defaultdict(
    lambda: """
.. literalinclude:: ../../../../../tensorbay/opendataset/{file_name}/catalog.json
   :language: json
   :name: {file_name}-catalog
   :linenos:
"""
)

_CATALOG_DESCRIPTIONS[
    "THCHS-30"
] = """However the catalog of THCHS-30 is too large, instead of
reading it from json file, we read it by mapping from subcatalog that is loaded by
the raw file. Check the :ref:`dataloader <THCHS30-dataloader>` below for more details.
"""

_INFORMATION_DESCRIPTIONS = defaultdict(
    lambda: """The information stored in
:ref:`reference/label_format/CommonLabelProperties:category` is one of the names in "categories"
list of :ref:`catalog.json <{file_name}-catalog>`. The information stored in
:ref:`reference/label_format/CommonLabelProperties:attributes` is one or several of
the attributes in "attributes" list of :ref:`catalog.json <{file_name}-catalog>`.
See :ref:`reference/label_format/{label_type}:{label_type}` label format for more details.
"""
)

_INFORMATION_DESCRIPTIONS[
    "THCHS-30"
] = """It contains ``sentence``, ``spell`` and ``phone``
information. See :ref:`Sentence <reference/label_format/{label_type}:{label_type}>` label
format for more details.
"""


def generate_examples_rst(example_path: str) -> None:
    """Generate rst flies in Examples.

    Arguments:
        example_path: The path of rst files in Examples.

    """
    os.makedirs(example_path, exist_ok=True)
    for dataset_name, label_type, file_name in zip(_DATASET_NAMES, _LABEL_TYPES, _FILE_NAMES):
        if dataset_name in _DATASET_WITH_IMAGES:
            figure_description_tmp = _FIGURE_DESCRIPTION.format(
                dataset_name=dataset_name, file_name=file_name, label_type=label_type
            )
        else:
            figure_description_tmp = ""
        catalog_description = _CATALOG_DESCRIPTIONS[dataset_name].format(file_name=file_name)
        information_description = _INFORMATION_DESCRIPTIONS[dataset_name].format(
            label_type=label_type, file_name=file_name
        )
        category_attribute_description = _CATEGORY_ATTRIBUTE_DESCRIPTIONS[dataset_name].format(
            dataset_name=dataset_name, label_type=label_type
        )
        with open(os.path.join(example_path, f"{file_name}.rst"), "w", encoding="utf-8") as fp:
            fp.write(
                EXAMPLES_TEMPLATE.format(
                    dataset_name=dataset_name,
                    file_name=file_name,
                    label_type=label_type,
                    figure_description=figure_description_tmp,
                    catalog_description=catalog_description,
                    category_attribute_description=category_attribute_description,
                    information_description=information_description,
                )
            )
