#!/usr/bin/env python3
#
# Copytright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloaders of the BDD100K dataset and the BDD100K_10K dataset."""

from tensorbay.opendataset.BDD100K.loader import BDD100K, BDD100K_10K

__all__ = ["BDD100K", "BDD100K_10K"]
