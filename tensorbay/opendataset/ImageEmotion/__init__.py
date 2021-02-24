#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=invalid-name

"""Dataloader of ImageEmotion."""

from .loader import ImageEmotionAbstract, ImageEmotionArtphoto

__all__ = ["ImageEmotionAbstract", "ImageEmotionArtphoto"]
