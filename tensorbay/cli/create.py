#!/usr/bin/env python3
#
# Copyright 2021 Graviti. All Rights Reserved.
#

"""Implementation of gas create."""

import sys
from typing import Dict

import click

from ..utility import TBRN, TBRNType
from .utility import get_gas


def _implement_create(obj: Dict[str, str], name: str) -> None:
    """Create a dataset.\f

    Arguments:
        obj: A dict including config information.
        name: The name of the dataset to be created, like "tb:KITTI".

    """  # noqa: D301,D415
    info = TBRN(tbrn=name)
    if info.type != TBRNType.DATASET:
        click.echo(f'"{name}" is not a dataset', err=True)
        sys.exit(1)
    get_gas(**obj).create_dataset(info.dataset_name)
