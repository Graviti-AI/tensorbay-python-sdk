#!/usr/bin/env python3
#
# Copyright 2021 Graviti. All Rights Reserved.
#

"""Implementation of gas delete."""

import sys
from typing import Dict

import click

from ..utility import TBRN, TBRNType
from .utility import get_gas


def _implement_delete(obj: Dict[str, str], name: str, yes: bool) -> None:
    """Delete a dataset.\f

    Arguments:
        obj: A dict including config info.
        name: The name of the dataset to be deleted, like "tb:KITTI".
        yes: Confirm to delete the dataset completely.

    """  # noqa: D301,D415
    info = TBRN(tbrn=name)
    if info.type != TBRNType.DATASET:
        click.echo(f'"{name}" is not a dataset', err=True)
        sys.exit(1)

    if not yes:
        click.confirm(
            f'Dataset "{name}" will be completely deleted.\nDo you want to continue?', abort=True
        )

    get_gas(**obj).delete_dataset(info.dataset_name)
