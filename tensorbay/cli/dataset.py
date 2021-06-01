#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas dataset."""

from typing import Dict

import click

from .tbrn import TBRN, TBRNType
from .utility import error, get_gas


def _implement_dataset(obj: Dict[str, str], tbrn: str, is_delete: bool, yes: bool) -> None:
    gas = get_gas(**obj)
    if is_delete:
        if not tbrn:
            error("Missing argument TBRN")

        info = TBRN(tbrn=tbrn)
        if info.type != TBRNType.DATASET:
            error(f'"{tbrn}" is not a dataset')

        if not yes:
            click.confirm(
                f'Dataset "{tbrn}" will be completely deleted.\nDo you want to continue?',
                abort=True,
            )

        gas.delete_dataset(info.dataset_name)
        click.echo(f'Dataset "{tbrn}" is deleted successfully')
        return

    if tbrn:
        info = TBRN(tbrn=tbrn)
        if info.type != TBRNType.DATASET:
            error(f'"{tbrn}" is not a dataset')

        gas.create_dataset(info.dataset_name)
        click.echo(f'Dataset "{tbrn}" is created successfully')
    else:
        for dataset_name in gas.list_dataset_names():
            click.echo(TBRN(dataset_name).get_tbrn())
