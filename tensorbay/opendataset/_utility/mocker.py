#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=missing-module-docstring, invalid-name

from typing import Any

from tensorbay.exception import ModuleImportError


class ImageMocker:
    """Raise import PIL error for data loader."""

    def __getattribute__(self, name: str) -> Any:
        raise ModuleImportError(module_name="pillow")


class xmltodictMocker:
    """Raise import xmltodict error for data loader."""

    def __getattribute__(self, name: str) -> Any:
        raise ModuleImportError(module_name="xmltodict")


Image = ImageMocker()
xmltodict = xmltodictMocker()
