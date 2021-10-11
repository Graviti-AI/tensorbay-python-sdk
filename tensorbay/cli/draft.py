#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas draft."""
from configparser import ConfigParser
from textwrap import indent
from typing import Optional, Tuple

import click

from tensorbay.cli.auth import INDENT
from tensorbay.cli.tbrn import TBRN, TBRNType
from tensorbay.cli.utility import (
    ContextInfo,
    edit_message,
    error,
    exception_handler,
    format_hint,
    get_dataset_client,
)
from tensorbay.client.gas import DatasetClientType
from tensorbay.client.struct import ROOT_COMMIT_ID

_DRAFT_HINT = """
# Please enter the message for your draft.
# Lines starting with '#' will be ignored.
# And an empty draft message aborts the creation.
"""

_FULL_DRAFT_MESSAGE = """Branch:{}{}

    {}
"""


@exception_handler
def _implement_draft(  # pylint: disable=too-many-arguments
    obj: ContextInfo,
    tbrn: str,
    is_list: bool,
    edit: bool,
    close: bool,
    message: Tuple[str, ...],
) -> None:
    gas = obj.get_gas()
    tbrn_info = TBRN(tbrn=tbrn)
    dataset_client = get_dataset_client(gas, tbrn_info)

    if tbrn_info.type != TBRNType.DATASET:
        error(f'To operate a draft, "{tbrn}" must be a dataset')

    if is_list:
        _list_drafts(dataset_client, tbrn_info)
    elif edit:
        _edit_draft(dataset_client, tbrn_info, message, obj.config_parser)
    elif close:
        _close_draft(dataset_client, tbrn_info)
    else:
        _create_draft(dataset_client, tbrn_info, message, obj.config_parser)


def _create_draft(
    dataset_client: DatasetClientType,
    tbrn_info: TBRN,
    message: Tuple[str, ...],
    config_parser: ConfigParser,
) -> None:
    if tbrn_info.is_draft:
        error(f'Create a draft in draft status "{tbrn_info.get_tbrn()}" is not permitted')

    title, description = edit_message(message, _DRAFT_HINT, config_parser)
    if not title:
        error("Aborting creating draft due to empty draft message")

    dataset_client.create_draft(title=title, description=description)
    status = dataset_client.status
    draft_tbrn = TBRN(tbrn_info.dataset_name, draft_number=status.draft_number).get_colored_tbrn()
    click.echo(f'Successfully created draft "{draft_tbrn}"')
    _echo_draft(dataset_client, title, description, status.branch_name)


def _list_drafts(dataset_client: DatasetClientType, tbrn_info: TBRN) -> None:
    if tbrn_info.revision:
        error(f'list drafts based on given revision "{tbrn_info.get_tbrn()}" is not supported')

    if tbrn_info.is_draft:
        draft = dataset_client.get_draft(tbrn_info.draft_number)
        click.echo(f"Draft: {tbrn_info.get_tbrn()}")
        _echo_draft(dataset_client, draft.title, draft.description, draft.branch_name)
    else:
        for draft in dataset_client.list_drafts():
            click.echo(
                f"Draft: {TBRN(tbrn_info.dataset_name, draft_number=draft.number).get_tbrn()}"
            )
            _echo_draft(dataset_client, draft.title, draft.description, draft.branch_name)


def _echo_draft(
    dataset_client: DatasetClientType,
    title: str = "",
    description: str = "",
    branch_name: Optional[str] = None,
) -> None:
    if not branch_name:
        error("Draft should be created based on a branch.")

    branch = dataset_client.get_branch(branch_name)

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


def _edit_draft(
    dataset_client: DatasetClientType,
    tbrn_info: TBRN,
    message: Tuple[str, ...],
    config_parser: ConfigParser,
) -> None:
    if not tbrn_info.is_draft:
        error("Draft number is required when editing draft")

    draft = dataset_client.get_draft()
    hint_message = format_hint(draft.title, draft.description, _DRAFT_HINT)
    title, description = edit_message(message, hint_message, config_parser)
    if not title:
        error("Aborting updating draft due to empty draft message")

    dataset_client.update_draft(title=title, description=description)
    click.echo(f'Successfully updated draft "{tbrn_info.get_colored_tbrn()}"')
    _echo_draft(dataset_client, title, description, dataset_client.status.branch_name)


def _close_draft(dataset_client: DatasetClientType, tbrn_info: TBRN) -> None:
    if not tbrn_info.draft_number:
        error("Draft number is required when editing draft")

    dataset_client._close_draft(tbrn_info.draft_number)  # pylint: disable=protected-access
    click.echo(f'Successfully closed draft "{tbrn_info.get_colored_tbrn()}"')
