#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloaders of 5 categories AnimalPose dataset and 7 categories AnimalPose dataset."""

from tensorbay.opendataset.AnimalPose.loader import AnimalPose5, AnimalPose7

__all__ = ["AnimalPose5", "AnimalPose7"]
