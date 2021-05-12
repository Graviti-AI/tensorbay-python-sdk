#!/usr/bin/env python3
#
# Copyright 2021 Graviti. All Rights Reserved.
#

"""Implementation of gas dataset."""

import sys
from typing import Dict

import click

from ..utility import TBRN, TBRNType
from .utility import get_gas


def _implement_dataset(obj: Dict[str, str], tbrn: str) -> None:
    gas = get_gas(**obj)
    if tbrn:
        info = TBRN(tbrn=tbrn)
        if info.type != TBRNType.DATASET:
            click.echo(f'"{tbrn}" is not a dataset', err=True)
            sys.exit(1)
        gas.create_dataset(info.dataset_name)
    else:
        for dataset_name in gas.list_dataset_names():
            click.echo(TBRN(dataset_name).get_tbrn())
