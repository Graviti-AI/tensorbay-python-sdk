#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas commit."""

from typing import Tuple

import click

from tensorbay.cli.tbrn import TBRN, TBRNType
from tensorbay.cli.utility import (
    ContextInfo,
    edit_message,
    error,
    exception_handler,
    format_hint,
    get_dataset_client,
)

_COMMIT_HINT = """
# Please enter the commit message for your changes.
# The Default commit message is set as the draft title.
# Lines starting with '#' will be ignored.
# And an empty commit message aborts the commit.
"""


@exception_handler
def _implement_commit(obj: ContextInfo, tbrn: str, message: Tuple[str, ...]) -> None:
    gas = obj.get_gas()
    tbrn_info = TBRN(tbrn=tbrn)
    dataset_client = get_dataset_client(gas, tbrn_info)

    if tbrn_info.type != TBRNType.DATASET:
        error(f'To operate a commit, "{tbrn}" must be a dataset')
    if not tbrn_info.is_draft:
        error(f'To commit, "{tbrn}" must be in draft status, like "{tbrn}#1"')

    dataset_client.checkout(draft_number=tbrn_info.draft_number)
    draft = dataset_client.get_draft()
    hint_message = format_hint(draft.title, draft.description, _COMMIT_HINT)
    title, description = edit_message(message, hint_message, obj.config_parser)
    if not title:
        error("Aborting commit due to empty commit message")

    dataset_client.commit(title, description)
    commit_tbrn = TBRN(tbrn_info.dataset_name, revision=dataset_client.status.commit_id)
    click.echo(
        "Committed successfully: "
        f"{tbrn_info.get_colored_tbrn()} -> {commit_tbrn.get_colored_tbrn()}"
    )
