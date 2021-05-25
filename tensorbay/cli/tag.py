#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas tag."""
import sys
from typing import Dict

import click

from ..client.gas import DatasetClientType
from .tbrn import TBRN, TBRNType
from .utility import get_dataset_client, get_gas


def _implement_tag(obj: Dict[str, str], tbrn: str) -> None:
    info = TBRN(tbrn=tbrn)

    if info.type != TBRNType.DATASET:
        click.echo(f'To operate a tag, "{info}" must be a dataset', err=True)
        sys.exit(1)

    gas = get_gas(**obj)
    dataset_client = get_dataset_client(gas, info)

    _list_tags(dataset_client)


def _list_tags(dataset_client: DatasetClientType) -> None:
    for tag in dataset_client.list_tags():
        click.echo(tag.name)
