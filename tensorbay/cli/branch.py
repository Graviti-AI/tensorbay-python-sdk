#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas branch."""

from typing import Dict

import click

from ..client.gas import DatasetClientType
from .tbrn import TBRN, TBRNType
from .utility import error, get_dataset_client, get_gas, shorten


def _implement_branch(
    obj: Dict[str, str], tbrn: str, name: str, verbose: bool, is_delete: bool
) -> None:
    info = TBRN(tbrn=tbrn)
    if info.type != TBRNType.DATASET:
        error(f'To operate a branch, "{info}" must be a dataset')

    gas = get_gas(**obj)
    dataset_client = get_dataset_client(gas, info)

    if is_delete:
        _delete_branch(dataset_client, info)
        return

    if name:
        _create_branch(dataset_client, name)
    else:
        _list_branches(dataset_client, verbose)


def _create_branch(dataset_client: DatasetClientType, name: str) -> None:
    if dataset_client.status.is_draft:
        error("Branch cannot be created from a draft")

    if not dataset_client.status.commit_id:
        error(f'To create a branch, "{dataset_client.name}" must have commit history')

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
            click.echo(f"{branch.name:{name_length}} {shorten(branch.commit_id)} {branch.title}")


def _delete_branch(dataset_client: DatasetClientType, info: TBRN) -> None:
    if not info.revision:
        error(f'To delete a branch, "{info}" must have a branch name')

    dataset_client._delete_branch(info.revision)  # pylint: disable=protected-access
    click.echo(f"{info} has been successfully deleted")
