#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas rm."""

from typing import Dict

import click

from .tbrn import TBRN, TBRNType
from .utility import error, get_dataset_client, get_gas


def _implement_rm(obj: Dict[str, str], tbrn: str, is_recursive: bool) -> None:
    gas = get_gas(**obj)
    info = TBRN(tbrn=tbrn)
    dataset_client = get_dataset_client(gas, info, is_fusion=False)

    if info.type not in (TBRNType.SEGMENT, TBRNType.NORMAL_FILE):
        error(f'"{tbrn}" is an invalid path to remove')

    if not info.is_draft:
        error(f'To remove the data, "{info}" must be in draft status, like "{info}#1"')

    if info.type == TBRNType.SEGMENT:
        if not is_recursive:
            error("Please use -r option to remove the whole segment")

        dataset_client.delete_segment(info.segment_name)
    else:
        segment = dataset_client.get_segment(info.segment_name)
        segment.delete_data(info.remote_path)

    click.echo(f"{tbrn} is deleted successfully")
