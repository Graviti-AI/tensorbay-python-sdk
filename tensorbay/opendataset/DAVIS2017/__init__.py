#!/usr/bin/env python3
#
# Copytright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloaders of the DAVIS2017Unsupervised dataset and DAVIS2017SemiSupervised dataset."""

from tensorbay.opendataset.DAVIS2017.loader import DAVIS2017SemiSupervised, DAVIS2017Unsupervised

__all__ = ["DAVIS2017Unsupervised", "DAVIS2017SemiSupervised"]
