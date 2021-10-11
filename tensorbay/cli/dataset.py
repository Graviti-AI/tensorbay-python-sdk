#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas dataset."""

import click

from tensorbay.cli.tbrn import TBRN, TBRNType
from tensorbay.cli.utility import ContextInfo, error, exception_handler


@exception_handler
def _implement_dataset(obj: ContextInfo, tbrn: str, is_delete: bool, yes: bool) -> None:
    gas = obj.get_gas()
    if not tbrn:
        if is_delete:
            error("Missing argument TBRN")
        for dataset_name in gas.list_dataset_names():
            click.echo(TBRN(dataset_name).get_tbrn())
        return

    tbrn_info = TBRN(tbrn=tbrn)
    if tbrn_info.type != TBRNType.DATASET:
        error(f'"{tbrn}" is not a dataset')
    colored_tbrn = tbrn_info.get_colored_tbrn()

    if is_delete:
        if not yes:
            click.confirm(
                f'Dataset "{colored_tbrn}" will be completely deleted.\nDo you want to continue?',
                abort=True,
            )

        gas.delete_dataset(tbrn_info.dataset_name)
        click.echo(f'Successfully deleted dataset "{colored_tbrn}"')
        return

    gas.create_dataset(tbrn_info.dataset_name)
    click.echo(f'Successfully created dataset "{colored_tbrn}"')
