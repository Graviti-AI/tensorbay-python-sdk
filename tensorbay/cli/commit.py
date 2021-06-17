#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas commit."""

from typing import Dict, Tuple

import click

from .tbrn import TBRN, TBRNType
from .utility import edit_input, error, get_dataset_client, get_gas

_COMMIT_HINT = """{}
# Please enter the commit message for your changes.
# The Default commit message is set as the draft title.
# Lines starting with '#' will be ignored.
# And an empty commit message aborts the commit.
"""


def _implement_commit(obj: Dict[str, str], tbrn: str, message: Tuple[str, ...]) -> None:
    gas = get_gas(**obj)
    info = TBRN(tbrn=tbrn)
    dataset_client = get_dataset_client(gas, info)

    if info.type != TBRNType.DATASET:
        error(f'To operate a commit, "{info}" must be a dataset')

    if not info.is_draft:
        error(f'To commit, "{info}" must be in draft status, like "{info}#1"')

    dataset_client.checkout(draft_number=info.draft_number)
    if message:
        title, description = message[0], "\n".join(message[1:])
    else:
        title, description = edit_input(_COMMIT_HINT.format(dataset_client.get_draft().title))

    if not title:
        error("Aborting commit due to empty commit message")

    dataset_client.commit(title, description)
    commit_tbrn = TBRN(info.dataset_name, revision=dataset_client.status.commit_id).get_tbrn()
    click.echo(f"Committed successfully: {tbrn} -> {commit_tbrn}")
