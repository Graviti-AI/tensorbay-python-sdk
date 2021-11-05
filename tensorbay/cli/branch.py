#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas branch."""

import click

from tensorbay.cli.tbrn import TBRN, TBRNType
from tensorbay.cli.utility import (
    ContextInfo,
    error,
    exception_handler,
    get_dataset_client,
    shorten,
    sort_branches_or_tags,
)
from tensorbay.client.gas import DatasetClientType


@exception_handler
def _implement_branch(  # pylint: disable=too-many-arguments
    obj: ContextInfo, tbrn: str, name: str, verbose: bool, is_delete: bool, sort_key: str
) -> None:
    tbrn_info = TBRN(tbrn=tbrn)
    if tbrn_info.type != TBRNType.DATASET:
        error(f'To operate a branch, "{tbrn_info}" must be a dataset')

    gas = obj.get_gas()
    dataset_client = get_dataset_client(gas, tbrn_info)

    if is_delete:
        _delete_branch(dataset_client, tbrn_info)
        return

    if name:
        _create_branch(dataset_client, name)
    else:
        _list_branches(dataset_client, verbose, sort_key)


def _create_branch(dataset_client: DatasetClientType, name: str) -> None:
    if dataset_client.status.is_draft:
        error("Branch cannot be created from a draft")

    dataset_client.create_branch(name)
    branch_tbrn = TBRN(dataset_client.name, revision=name).get_colored_tbrn()
    click.echo(f'Successfully created branch "{branch_tbrn}"')


def _list_branches(dataset_client: DatasetClientType, verbose: bool, sort_key: str) -> None:
    branches = sort_branches_or_tags(sort_key, dataset_client.list_branches())
    if not verbose:
        for branch in branches:
            click.echo(branch.name)
    else:
        name_length = max(len(branch.name) for branch in branches)
        for branch in branches:
            click.echo(f"{branch.name:{name_length}} {shorten(branch.commit_id)} {branch.title}")


def _delete_branch(dataset_client: DatasetClientType, tbrn_info: TBRN) -> None:
    if not tbrn_info.revision:
        error(f'To delete a branch, "{tbrn_info.get_tbrn()}" must have a branch name')

    dataset_client._delete_branch(tbrn_info.revision)  # pylint: disable=protected-access
    click.echo(f'Successfully deleted branch "{tbrn_info.get_colored_tbrn()}"')
