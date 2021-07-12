#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas draft."""

from textwrap import indent
from typing import Dict, Optional, Tuple

import click

from ..client.gas import DatasetClientType
from ..client.struct import ROOT_COMMIT_ID
from ..exception import ResourceNotExistError
from .auth import INDENT
from .tbrn import TBRN, TBRNType
from .utility import edit_message, error, format_hint, get_dataset_client, get_gas

_DRAFT_HINT = """
# Please enter the message for your draft.
# Lines starting with '#' will be ignored.
# And an empty draft message aborts the creation.
"""

_FULL_DRAFT_MESSAGE = """Branch:{}{}

    {}
"""


def _implement_draft(  # pylint: disable=too-many-arguments
    obj: Dict[str, str], tbrn: str, is_list: bool, edit: bool, close: bool, message: Tuple[str, ...]
) -> None:
    gas = get_gas(**obj)
    info = TBRN(tbrn=tbrn)
    dataset_client = get_dataset_client(gas, info)

    if info.type != TBRNType.DATASET:
        error(f'To operate a draft, "{info}" must be a dataset')

    if is_list:
        _list_drafts(dataset_client, info)
    elif edit:
        _edit_draft(dataset_client, info, message)
    elif close:
        _close_draft(dataset_client, info)
    else:
        _create_draft(dataset_client, info, message)


def _create_draft(dataset_client: DatasetClientType, info: TBRN, message: Tuple[str, ...]) -> None:
    if info.is_draft:
        error(f'Create a draft in draft status "{info}" is not permitted')

    title, description = edit_message(message, _DRAFT_HINT)
    if not title:
        error("Aborting creating draft due to empty draft message")

    dataset_client.create_draft(title=title, description=description)
    status = dataset_client.status
    draft_tbrn = TBRN(info.dataset_name, draft_number=status.draft_number).get_tbrn()
    click.echo(f"{draft_tbrn} is created successfully")
    _echo_draft(dataset_client, title, description, status.branch_name)


def _list_drafts(dataset_client: DatasetClientType, info: TBRN) -> None:
    if info.revision:
        error(f'list drafts based on given revision "{info}" is not supported')

    if info.is_draft:
        draft = dataset_client.get_draft(info.draft_number)
        click.echo(f"Draft: {info.get_tbrn()}")
        _echo_draft(dataset_client, draft.title, draft.description, draft.branch_name)
    else:
        for draft in dataset_client.list_drafts():
            click.echo(f"Draft: {TBRN(info.dataset_name, draft_number=draft.number).get_tbrn()}")
            _echo_draft(dataset_client, draft.title, draft.description, draft.branch_name)


def _echo_draft(
    dataset_client: DatasetClientType,
    title: str = "",
    description: str = "",
    branch_name: Optional[str] = None,
) -> None:
    if not branch_name:
        error("Draft should be created based on a branch.")

    try:
        branch = dataset_client.get_branch(branch_name)
    except ResourceNotExistError:
        error(f'The branch "{branch_name}" does not exist')

    if branch.commit_id != ROOT_COMMIT_ID:
        commit_id = f"({branch.commit_id})"
    else:
        commit_id = ""

    if not title:
        title = "<no title>"
    if description:
        description = f"\n\n{indent(description, INDENT)}"
    draft_message = f"{title}{description}"
    click.echo(
        _FULL_DRAFT_MESSAGE.format(
            branch_name,
            commit_id,
            draft_message,
        )
    )


def _edit_draft(dataset_client: DatasetClientType, info: TBRN, message: Tuple[str, ...]) -> None:
    if not info.is_draft:
        error("Draft number is required when editing draft")

    draft = dataset_client.get_draft()
    hint_message = format_hint(draft.title, draft.description, _DRAFT_HINT)
    title, description = edit_message(message, hint_message)
    if not title:
        error("Aborting updating draft due to empty draft message")

    dataset_client.update_draft(title=title, description=description)
    click.echo(f"{info.get_tbrn()} is updated successfully!")
    _echo_draft(dataset_client, title, description, dataset_client.status.branch_name)


def _close_draft(dataset_client: DatasetClientType, info: TBRN) -> None:
    if not info.is_draft:
        error("Draft number is required when editing draft")

    dataset_client.close_draft()
    click.echo(f"{info.get_tbrn()} is closed.")
