#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas draft."""

from typing import Dict, Optional, Tuple

import click

from ..client.gas import DatasetClientType
from ..client.struct import ROOT_COMMIT_ID
from ..exception import ResourceNotExistError
from .tbrn import TBRN, TBRNType
from .utility import edit_input, error, get_dataset_client, get_gas

_DRAFT_HINT = """
# Please enter the title for your draft.
# Lines starting with '#' will be ignored.
# And an empty draft title aborts the creation.
"""


def _implement_draft(
    obj: Dict[str, str], tbrn: str, is_list: bool, message: Tuple[str, ...]
) -> None:
    gas = get_gas(**obj)
    info = TBRN(tbrn=tbrn)
    dataset_client = get_dataset_client(gas, info)

    if info.type != TBRNType.DATASET:
        error(f'To operate a draft, "{info}" must be a dataset')

    if is_list:
        _list_drafts(dataset_client, info)
    else:
        _create_draft(dataset_client, info, message)


def _create_draft(dataset_client: DatasetClientType, info: TBRN, message: Tuple[str, ...]) -> None:
    if info.is_draft:
        error(f'Create a draft in draft status "{info}" is not permitted')

    if message:
        title, description = message[0], "\n".join(message[1:])
    else:
        title, description = edit_input(_DRAFT_HINT)

    if description:
        error('Creating draft with "description" is not supported yet')

    if not title:
        error("Aborting creating draft due to empty draft title")

    dataset_client.create_draft(title=title)
    status = dataset_client.status
    draft_tbrn = TBRN(info.dataset_name, draft_number=status.draft_number).get_tbrn()
    click.echo(f"{draft_tbrn} is created successfully")
    _echo_draft(dataset_client, title, status.branch_name)


def _list_drafts(dataset_client: DatasetClientType, info: TBRN) -> None:
    if info.revision:
        error(f'list drafts based on given revision "{info}" is not supported')

    if info.is_draft:
        draft = dataset_client.get_draft(info.draft_number)
        click.echo(f"Draft: {info.get_tbrn()}")
        _echo_draft(dataset_client, draft.title, draft.branch_name)
    else:
        for draft in dataset_client.list_drafts():
            click.echo(f"Draft: {TBRN(info.dataset_name, draft_number=draft.number).get_tbrn()}")
            _echo_draft(dataset_client, draft.title, draft.branch_name)


def _echo_draft(
    dataset_client: DatasetClientType, title: str = "", branch_name: Optional[str] = None
) -> None:
    if not branch_name:
        error("Draft should be created based on a branch.")

    try:
        branch = dataset_client.get_branch(branch_name)
    except ResourceNotExistError:
        error('The branch "{branch_name}" does not exist')

    if branch.commit_id != ROOT_COMMIT_ID:
        click.echo(f"Branch: {branch_name}({branch.commit_id})")
    else:
        click.echo(f"Branch: {branch_name}")

    if not title:
        title = "<no title>"
    click.echo(f"\n    {title}\n")
