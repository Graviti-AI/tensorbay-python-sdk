#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas log."""

from datetime import datetime
from textwrap import indent
from typing import Dict, Optional

import click

from ..client.struct import Commit
from .auth import INDENT
from .tbrn import TBRN
from .utility import get_dataset_client, get_gas, shorten

_FULL_LOG = """commit {}
Author: {}
Date: {}

    {}
"""


def _implement_log(
    obj: Dict[str, str],
    tbrn: str,
    max_count: Optional[int],
    oneline: bool,
) -> None:
    gas = get_gas(**obj)
    info = TBRN(tbrn=tbrn)
    dataset_client = get_dataset_client(gas, info)

    commits = dataset_client.list_commits(info.revision)[:max_count]
    template = _get_oneline_log if oneline else _get_full_log
    click.echo_via_pager(template(commit) for commit in commits)


def _get_oneline_log(commit: Commit) -> str:
    return f"{shorten(commit.commit_id)} {commit.title}\n"


def _get_full_log(commit: Commit) -> str:
    description = commit.description
    if description:
        description = f"\n\n{indent(description, INDENT)}"
    commit_message = f"{commit.title}{description}\n"
    return _FULL_LOG.format(
        commit.commit_id,
        commit.committer.name,
        datetime.fromtimestamp(commit.committer.date).strftime("%a %b %d %H:%M:%S %y"),
        commit_message,
    )
