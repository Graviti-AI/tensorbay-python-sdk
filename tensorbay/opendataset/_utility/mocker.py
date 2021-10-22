#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=missing-module-docstring, invalid-name

from tensorbay.exception import ModuleImportError


class Image:
    """Raise import PIL error for data loader."""

    def __getattribute__(self, name: str) -> None:
        raise ModuleImportError(module_name="pillow")


class xmltodict:
    """Raise import xmltodict error for data loader."""

    def __getattribute__(self, name: str) -> None:
        raise ModuleImportError(module_name="xmltodict")
