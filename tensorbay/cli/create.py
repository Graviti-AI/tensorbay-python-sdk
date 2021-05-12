#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas create."""

import sys
from typing import Dict

import click

from ..utility import TBRN, TBRNType
from .utility import get_gas


def _implement_create(obj: Dict[str, str], name: str) -> None:
    info = TBRN(tbrn=name)
    if info.type != TBRNType.DATASET:
        click.echo(f'"{name}" is not a dataset', err=True)
        sys.exit(1)
    get_gas(**obj).create_dataset(info.dataset_name)
