#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas tag."""

from typing import Dict

import click

from ..client.gas import DatasetClientType
from .tbrn import TBRN, TBRNType
from .utility import error, get_dataset_client, get_gas


def _implement_tag(obj: Dict[str, str], tbrn: str, name: str, is_delete: bool) -> None:
    info = TBRN(tbrn=tbrn)

    if info.type != TBRNType.DATASET:
        error(f'To operate a tag, "{info}" must be a dataset')

    gas = get_gas(**obj)
    dataset_client = get_dataset_client(gas, info)

    if is_delete:
        _delete_tag(dataset_client, info)
    elif name:
        _create_tag(dataset_client, name)
    else:
        _list_tags(dataset_client)


def _delete_tag(dataset_client: DatasetClientType, info: TBRN) -> None:
    if not info.revision:
        error(f'To delete a tag, "{info}" must have a tag name')

    dataset_client.delete_tag(info.revision)
    tag_tbrn = TBRN(dataset_client.name, revision=info.revision).get_tbrn()
    click.echo(f"{tag_tbrn} is deleted successfully")


def _create_tag(dataset_client: DatasetClientType, name: str) -> None:
    if dataset_client.status.is_draft:
        error(f'To create a tag, "{dataset_client.name}" cannot be in draft status')

    if not dataset_client.status.commit_id:
        error(f'To create a tag, "{dataset_client.name}" should have commit history')

    dataset_client.create_tag(name=name)
    tag_tbrn = TBRN(dataset_client.name, revision=name).get_tbrn()
    click.echo(f"{tag_tbrn} is created successfully")


def _list_tags(dataset_client: DatasetClientType) -> None:
    for tag in dataset_client.list_tags():
        click.echo(tag.name)
