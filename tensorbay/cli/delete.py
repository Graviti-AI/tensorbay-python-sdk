#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas delete."""

import sys
from typing import Dict

import click

from .tbrn import TBRN, TBRNType
from .utility import get_gas


def _implement_delete(obj: Dict[str, str], name: str, yes: bool) -> None:
    info = TBRN(tbrn=name)
    if info.type != TBRNType.DATASET:
        click.echo(f'"{name}" is not a dataset', err=True)
        sys.exit(1)

    if not yes:
        click.confirm(
            f'Dataset "{name}" will be completely deleted.\nDo you want to continue?', abort=True
        )

    get_gas(**obj).delete_dataset(info.dataset_name)
