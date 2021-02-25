#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of the Kenyan Food or Nonfood dataset and Kenyan Food Type dataset."""

from .loader import KenyanFoodOrNonfood, KenyanFoodType

__all__ = ["KenyanFoodOrNonfood", "KenyanFoodType"]
