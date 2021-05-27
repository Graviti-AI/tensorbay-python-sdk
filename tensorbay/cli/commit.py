#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas commit."""

import sys
from typing import Dict

import click

from .tbrn import TBRN, TBRNType
from .utility import edit_input, get_dataset_client, get_gas

_COMMIT_HINT = """{}
# Please enter the commit message for your changes.
# The Default commit message is set as the draft title.
# Lines starting with '#' will be ignored.
# And an empty commit message aborts the commit.
"""


def _implement_commit(obj: Dict[str, str], tbrn: str, message: str) -> None:
    gas = get_gas(**obj)
    info = TBRN(tbrn=tbrn)
    dataset_client = get_dataset_client(gas, info)

    if info.type != TBRNType.DATASET:
        click.echo(f'To operate a commit, "{info}" must be a dataset', err=True)
        sys.exit(1)

    if not info.is_draft:
        click.echo(f'To commit, "{info}" must be in draft status, like "{info}#1"', err=True)
        sys.exit(1)

    dataset_client.checkout(draft_number=info.draft_number)
    if not message:
        message, description = edit_input(_COMMIT_HINT.format(dataset_client.get_draft().title))

    if not message:
        click.echo("Aborting commit due to empty commit message", err=True)
        sys.exit(1)

    if description:
        click.echo('Commit with "description" is not supported yet', err=True)
        sys.exit(1)

    dataset_client.commit(message)
    commit_tbrn = TBRN(info.dataset_name, revision=dataset_client.status.commit_id).get_tbrn()
    click.echo(f"Committed successfully: {tbrn} -> {commit_tbrn}")
