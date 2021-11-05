#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas tag."""

import click

from tensorbay.cli.tbrn import TBRN, TBRNType
from tensorbay.cli.utility import (
    ContextInfo,
    error,
    exception_handler,
    get_dataset_client,
    sort_branches_or_tags,
)
from tensorbay.client.gas import DatasetClientType


@exception_handler
def _implement_tag(obj: ContextInfo, tbrn: str, name: str, is_delete: bool, sort_key: str) -> None:
    tbrn_info = TBRN(tbrn=tbrn)

    if tbrn_info.type != TBRNType.DATASET:
        error(f'To operate a tag, "{tbrn}" must be a dataset')

    gas = obj.get_gas()
    dataset_client = get_dataset_client(gas, tbrn_info)

    if is_delete:
        _delete_tag(dataset_client, tbrn_info)
    elif name:
        _create_tag(dataset_client, name)
    else:
        _list_tags(dataset_client, sort_key)


def _delete_tag(dataset_client: DatasetClientType, tbrn_info: TBRN) -> None:
    if not tbrn_info.revision:
        error(f'To delete a tag, "{tbrn_info.get_tbrn()}" must have a tag name')

    dataset_client.delete_tag(tbrn_info.revision)
    tag_tbrn = TBRN(dataset_client.name, revision=tbrn_info.revision).get_colored_tbrn()
    click.echo(f'Successfully deleted tag "{tag_tbrn}"')


def _create_tag(dataset_client: DatasetClientType, name: str) -> None:
    if dataset_client.status.is_draft:
        error(f'To create a tag, "{dataset_client.name}" cannot be in draft status')

    if not dataset_client.status.commit_id:
        error(f'To create a tag, "{dataset_client.name}" should have commit history')

    dataset_client.create_tag(name=name)
    tag_tbrn = TBRN(dataset_client.name, revision=name).get_colored_tbrn()
    click.echo(f'Successfully created tag "{tag_tbrn}"')


def _list_tags(dataset_client: DatasetClientType, sort_key: str) -> None:
    for tag in sort_branches_or_tags(sort_key, dataset_client.list_tags()):
        click.echo(tag.name)
