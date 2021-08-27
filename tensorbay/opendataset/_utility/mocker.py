#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=missing-module-docstring

from ...exception import ModuleImportError


class Image:
    """Raise import PIL error for data loader."""

    def __getattribute__(self, name: str) -> None:
        raise ModuleImportError(module_name="pillow")
