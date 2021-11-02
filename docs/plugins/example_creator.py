#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=no-value-for-parameter
# pylint: disable=too-many-instance-attributes

"""This file generates examples/*.rst with dataset names listed in examples.rst."""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_PATH = str(Path(os.path.abspath(__file__)).parents[2])
sys.path.insert(0, REPO_PATH)

from tensorbay import GAS  # noqa: E402
from tensorbay.dataset import Segment  # noqa: E402


class ExampleCreator:
    """Create an dataset management example."""

    _OPEN_DATASETS_PATH = os.path.join(REPO_PATH, "tensorbay", "opendataset")
    _SOURCE_PATH = os.path.join(REPO_PATH, "docs", "source")
    _EXAMPLES_PATH = os.path.join(_SOURCE_PATH, "examples")
    _IMAGES_PATH = os.path.join(_SOURCE_PATH, "images")
    _TEMPLATE_PATH = os.path.join(_EXAMPLES_PATH, "template.json")
    _EXAMPLES_RST_PATH = os.path.join(_SOURCE_PATH, "quick_start", "examples.rst")

    _TOPMOST_TITLE_LEVEL = 0
    _EXAMPLE_TITLES = {
        "authorization": "Authorize a Client Instance",
        "create_dataset": "Create Dataset",
        "organize_dataset": "Organize Dataset",
        "upload_dataset": "Upload Dataset",
        "read_dataset": "Read Dataset",
        "read_label": "Read Label",
        "delete_dataset": "Delete Dataset",
    }

    def __init__(self, access_key: str, name: str, alias: str) -> None:
        self._access_key = access_key
        self._name = name
        self._alias = alias
        self._dataset_path = os.path.join(self._OPEN_DATASETS_PATH, self._name)
        self._is_catalog_existed = os.path.exists(os.path.join(self._dataset_path, "catalog.json"))
        self._dataset_client = GAS(self._access_key).get_dataset(self._name)
        self._label_types = self._get_label_types()
        self._segment_names = self._dataset_client.list_segment_names()
        self._template = self._get_template()
        self._content: List[str] = []

        self._load_content()

    def dump_content(self) -> None:
        """Dump the content in an example file."""
        with open(os.path.join(self._EXAMPLES_PATH, f"{self._name}.rst"), "w") as fp:
            fp.write("".join(self._content))

    def _get_template(self) -> Dict[str, Any]:
        with open(self._TEMPLATE_PATH, "r") as fp:
            template_ = fp.read()
        template_name_replaced = template_.replace("<dataset_name>", self._name)
        template_alias_replaced = template_name_replaced.replace("<dataset_alias>", self._alias)
        template: Dict[str, Any] = json.loads(template_alias_replaced)
        return template

    def _load_content(self) -> None:
        self._load_top()
        self._load_authorization()
        self._load_create_dataset()
        self._load_organize_dataset()
        self._load_upload_dataset()
        self._load_read_dataset()
        self._load_read_label()
        self._load_delete_dataset()

    def _load_top(self) -> None:
        self._create_and_add_title(self._alias, self._TOPMOST_TITLE_LEVEL)
        lines = self._template[self._name]
        self._content.append(lines["head"].replace("<label_types>", self._organize_label_types()))
        if os.path.exists(os.path.join(self._IMAGES_PATH, f"{self._name}.png")):
            self._content.append(lines["with-image"])
        else:
            self._content.append(lines["without-image"])

    def _create_and_add_title(self, title: str, title_level: int) -> None:
        char = "#" if title_level == 0 else "*"
        decorator_line = char * (len(title) + 2)
        self._content.append(f"{decorator_line}\n {title} \n{decorator_line}\n\n")

    def _organize_label_types(self) -> str:
        if len(self._label_types) == 1:
            return self._label_types[0]

        return f'{", ".join(self._label_types[:-1])} and {self._label_types[-1]})'

    def _get_label_types(self) -> List[str]:
        label_types = self._dataset_client.get_catalog().dumps().keys()
        capitalized_types = [type_.capitalize() for type_ in label_types]
        for index, type_ in enumerate(capitalized_types):
            capitalized_types[index] = type_[:-1] + "D" if re.search(r"\dd", type_) else type_
        return capitalized_types

    def _load_authorization(self) -> None:
        self._assemble(self._EXAMPLE_TITLES["authorization"], self._TOPMOST_TITLE_LEVEL + 1)

    def _assemble(self, key: str, title_level: int) -> None:
        self._create_and_add_title(key, title_level)
        self._content.append(self._template[key])

    def _load_create_dataset(self) -> None:
        self._assemble(self._EXAMPLE_TITLES["create_dataset"], self._TOPMOST_TITLE_LEVEL + 1)

    def _load_organize_dataset(self) -> None:
        key = self._EXAMPLE_TITLES["organize_dataset"]
        self._create_and_add_title(key, self._TOPMOST_TITLE_LEVEL + 1)
        lines = self._template[key]
        self._content.append(lines["head"])
        self._content.append(
            lines["with catalog"] if self._is_catalog_existed else lines["without catalog"]
        )
        self._content.append(self._replace_label_classes(lines["tail"]))

    def _replace_label_classes(self, line: str) -> str:
        loader_path = os.path.join(self._dataset_path, "loader.py")
        with open(loader_path, "r") as fp:
            loader_lines = fp.readlines()

        for loader_line in loader_lines:
            if loader_line.startswith("from ...label"):
                label_classes = loader_line.split(" import ")[1]

        return line.replace("<label_classes>", label_classes)

    def _load_upload_dataset(self) -> None:
        self._assemble(self._EXAMPLE_TITLES["upload_dataset"], self._TOPMOST_TITLE_LEVEL + 1)

    def _load_read_dataset(self) -> None:
        key = self._EXAMPLE_TITLES["read_dataset"]
        self._create_and_add_title(key, self._TOPMOST_TITLE_LEVEL + 1)
        lines = self._template[key]

        self._content.append(self._replace_segments(lines["get_dataset"]))
        if len(self._segment_names) > 1:
            self._content.append(lines["list_segments"])
        self._content.append(self._replace_read_segment(lines["get_segment"]))

    def _replace_segments(self, line: str) -> str:
        segment_number = len(self._segment_names)
        if segment_number == 1:
            description = line.replace("<segment_number>", "is 1 :ref:`segment")
            if self._segment_names[0] == "":
                return description.replace("<segments>", '``""`` (an empty string)')

            return description.replace("<segments>", "``{name}``")

        description = line.replace("<segment_number>", f"are {str(segment_number)} :ref:`segments")
        return description.replace("<segments>", self._format_segment_names())

    def _format_segment_names(self) -> str:
        description = ", ".join([f"``{name}``" for name in self._segment_names[:-1]])
        return f"{description} and ``{self._segment_names[-1]}``"

    def _replace_read_segment(self, line: str) -> str:
        for name in self._segment_names:
            segment = Segment(name, self._dataset_client)
            data = segment[0]
            has_all_types_of_labels = True
            for label_type in self._label_types:
                if not hasattr(data.label, label_type.lower()):
                    has_all_types_of_labels = False
                    break
            if has_all_types_of_labels:
                return line.replace("<segment_name>", name)

        raise ValueError("No segment has all label types.")

    def _load_read_label(self) -> None:
        key = self._EXAMPLE_TITLES["read_label"]
        for type_ in self._label_types:
            self._content.append(self._template[key]["head"].replace("<label_type>", type_))
            self._content.append(self._template[key][type_])
        self._content.append(self._template[key]["tail"])

    def _load_delete_dataset(self) -> None:
        self._assemble(self._EXAMPLE_TITLES["delete_dataset"], self._TOPMOST_TITLE_LEVEL + 1)

    @classmethod
    def generate_examples(cls) -> None:
        """Generate example rst files automatically based on the example table in examples.rst."""
        print("Creating dataset management examples...")
        for name, alias in cls.get_dataset_names_and_aliases():
            print(f"\t--{name}")
            access_key = os.environ["ACCESS_KEY"]
            example_creator = cls(access_key, name, alias)
            example_creator.dump_content()

    @classmethod
    def get_dataset_names_and_aliases(cls) -> List[List[str]]:
        """Get all dataset names and aliases in quick_start/examples.rst.

        Returns:
            A list contains all the names and aliases.
        """
        with open(cls._EXAMPLES_RST_PATH, "r") as fp:
            examples_lines = fp.readlines()
        valid_lines = filter(
            lambda line: line.strip().endswith("Dataset Management"), examples_lines
        )
        return [line.split("`")[1].split("/")[1].split(":") for line in valid_lines]


if __name__ == "__main__":
    ExampleCreator.generate_examples()
