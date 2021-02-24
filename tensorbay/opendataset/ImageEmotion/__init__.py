#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#
# pylint: disable=invalid-name

"""Dataloader of ImageEmotion."""

from .loader import ImageEmotionAbstract, ImageEmotionArtphoto

__all__ = ["ImageEmotionAbstract", "ImageEmotionArtphoto"]
