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


def _implement_branch(obj: Dict[str, str], tbrn: str, name: str, verbose: bool) -> None:
    info = TBRN(tbrn=tbrn)

    if info.type != TBRNType.DATASET:
        click.echo(f'To operate a branch, "{info}" must be a dataset', err=True)
        sys.exit(1)

    gas = get_gas(**obj)
    dataset_client = get_dataset_client(gas, info)

    if name:
        _create_branch(dataset_client, name)
    else:
        _list_branches(dataset_client, verbose)


def _create_branch(dataset_client: DatasetClientType, name: str) -> None:
    if dataset_client.status.is_draft:
        click.echo("Branch cannot be created from a draft", err=True)
        sys.exit(1)

    if not dataset_client.status.commit_id:
        click.echo(
            f'To create a branch, "{dataset_client.name}" must have commit history', err=True
        )
        sys.exit(1)

    dataset_client.create_branch(name)
    branch_tbrn = TBRN(dataset_client.name, revision=name)
    click.echo(f"{branch_tbrn} has been successfully created")


def _list_branches(dataset_client: DatasetClientType, verbose: bool) -> None:
    branches = dataset_client.list_branches()
    if not verbose:
        for branch in branches:
            click.echo(branch.name)
    else:
        name_length = max(len(branch.name) for branch in branches)
        for branch in branches:
            click.echo(f"{branch.name:{name_length}} {branch.commit_id[:7]} {branch.message}")
