#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of the 17 Category Flower dataset and the 102 Category Flower dataset."""

from .loader import Flower17, Flower102

__all__ = ["Flower17", "Flower102"]
