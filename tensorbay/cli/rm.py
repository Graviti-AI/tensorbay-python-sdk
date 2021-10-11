#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas rm."""

import click

from tensorbay.cli.tbrn import TBRN, TBRNType
from tensorbay.cli.utility import ContextInfo, error, exception_handler, get_dataset_client


@exception_handler
def _implement_rm(obj: ContextInfo, tbrn: str, is_recursive: bool) -> None:
    gas = obj.get_gas()
    tbrn_info = TBRN(tbrn=tbrn)
    dataset_client = get_dataset_client(gas, tbrn_info, is_fusion=False)

    if tbrn_info.type not in (TBRNType.SEGMENT, TBRNType.NORMAL_FILE):
        error(f'"{tbrn}" is an invalid path to remove')

    if not tbrn_info.is_draft:
        error(f'To remove the data, "{tbrn}" must be in draft status, like "{tbrn}#1"')

    if tbrn_info.type == TBRNType.SEGMENT:
        if not is_recursive:
            error("Please use -r option to remove the whole segment")

        dataset_client.delete_segment(tbrn_info.segment_name)
    else:
        segment = dataset_client.get_segment(tbrn_info.segment_name)
        segment.delete_data(tbrn_info.remote_path)

    click.echo(f'Successfully deleted "{tbrn_info.get_colored_tbrn()}"')
