#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas draft."""

import sys
from typing import Dict

import click

from ..client.gas import DatasetClientType
from ..exception import ResourceNotExistError
from .tbrn import TBRN, TBRNType
from .utility import get_dataset_client, get_gas


def _implement_draft(obj: Dict[str, str], tbrn: str, is_list: bool, title: str) -> None:
    gas = get_gas(**obj)
    info = TBRN(tbrn=tbrn)
    dataset_client = get_dataset_client(gas, info)

    if info.type != TBRNType.DATASET:
        click.echo(f'To operate a draft, "{info}" must be a dataset', err=True)
        sys.exit(1)

    if is_list:
        _list_drafts(dataset_client, info)
    else:
        # todo: create draft base on revision
        _create_draft(dataset_client, info, title)


def _create_draft(dataset_client: DatasetClientType, info: TBRN, title: str) -> None:
    if info.is_draft:
        click.echo(f'Create a draft in draft status "{info}" is not permitted', err=True)
        sys.exit(1)

    if info.revision:
        click.echo(f'Create a draft based on given revision "{info}" is not supported', err=True)
        sys.exit(1)

    dataset_client.create_draft(title=title)
    draft_tbrn = TBRN(info.dataset_name, draft_number=dataset_client.status.draft_number).get_tbrn()
    click.echo(f"{draft_tbrn} is created successfully")
    _echo_draft(dataset_client, title)


def _list_drafts(dataset_client: DatasetClientType, info: TBRN) -> None:
    if info.revision:
        click.echo(f'list drafts based on given revision "{info}" is not supported', err=True)
        sys.exit(1)

    if info.is_draft:
        draft = dataset_client.get_draft(info.draft_number)
        click.echo(f"Draft: {TBRN(info.dataset_name, draft_number=draft.number).get_tbrn()}")
        _echo_draft(dataset_client, title=draft.title)
    else:
        for draft in dataset_client.list_drafts():
            click.echo(f"Draft: {TBRN(info.dataset_name, draft_number=draft.number).get_tbrn()}")
            _echo_draft(dataset_client, title=draft.title)


def _echo_draft(dataset_client: DatasetClientType, title: str = "") -> None:
    try:
        click.echo(f"Branch: main({dataset_client.get_commit('main').commit_id}) -> main")
    except ResourceNotExistError:
        click.echo("Branch: main -> main\n")

    if not title:
        title = "<no title>"
    click.echo(f"    {title}\n")
