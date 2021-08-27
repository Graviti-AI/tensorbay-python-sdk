#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas dataset."""

import click

from .tbrn import TBRN, TBRNType
from .utility import ContextInfo, error, exception_handler, get_gas


@exception_handler
def _implement_dataset(obj: ContextInfo, tbrn: str, is_delete: bool, yes: bool) -> None:
    gas = get_gas(*obj)
    if not tbrn:
        if is_delete:
            error("Missing argument TBRN")
        for dataset_name in gas.list_dataset_names():
            click.echo(TBRN(dataset_name).get_tbrn())

    info = TBRN(tbrn=tbrn)
    if info.type != TBRNType.DATASET:
        error(f'"{tbrn}" is not a dataset')
    colored_tbrn = info.get_colored_tbrn()

    if is_delete:
        if not yes:
            click.confirm(
                f'Dataset "{colored_tbrn}" will be completely deleted.\nDo you want to continue?',
                abort=True,
            )

        gas.delete_dataset(info.dataset_name)
        click.echo(f'Successfully deleted dataset "{colored_tbrn}"')
        return

    gas.create_dataset(info.dataset_name)
    click.echo(f'Successfully created dataset "{colored_tbrn}"')
