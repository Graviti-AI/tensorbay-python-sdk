#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas branch."""

import sys
from typing import Dict

import click

from ..client.gas import DatasetClientType
from .tbrn import TBRN, TBRNType
from .utility import get_dataset_client, get_gas


def _implement_branch(obj: Dict[str, str], tbrn: str, verbose: bool) -> None:
    info = TBRN(tbrn=tbrn)

    if info.type != TBRNType.DATASET:
        click.echo(f'To operate a branch, "{info}" must be a dataset', err=True)
        sys.exit(1)

    gas = get_gas(**obj)
    dataset_client = get_dataset_client(gas, info)

    _list_branches(dataset_client, verbose)


def _list_branches(dataset_client: DatasetClientType, verbose: bool) -> None:
    branches = dataset_client.list_branches()
    if not verbose:
        for branch in branches:
            click.echo(branch.name)
    else:
        name_length = max(len(branch.name) for branch in branches)
        for branch in branches:
            click.echo(f"{branch.name:{name_length}} {branch.commit_id[:7]} {branch.message}")
