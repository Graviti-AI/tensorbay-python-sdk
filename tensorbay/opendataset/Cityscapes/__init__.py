#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloaders of the CityscapesGTCoarse dataset and the CityscapesGTFine dataset."""

from tensorbay.opendataset.Cityscapes.loader import CityscapesGTCoarse, CityscapesGTFine

__all__ = ["CityscapesGTCoarse", "CityscapesGTFine"]
