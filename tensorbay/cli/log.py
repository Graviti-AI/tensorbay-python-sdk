#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas log."""

from datetime import datetime
from typing import Callable, Dict, Optional

import click

from ..client.struct import Commit
from .tbrn import TBRN
from .utility import get_dataset_client, get_gas

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
    graph: bool,
) -> None:
    gas = get_gas(**obj)
    info = TBRN(tbrn=tbrn)
    dataset_client = get_dataset_client(gas, info)

    commits = dataset_client.list_commits(info.revision)[:max_count]
    template: Callable[[Commit], str]
    template = _get_oneline_log if oneline else _get_full_log
    if graph:
        template = _add_graph(template)
    click.echo_via_pager(template(commit) for commit in commits)


def _get_oneline_log(commit: Commit) -> str:
    return f"{commit.commit_id[:7]} {commit.message}\n"


def _get_full_log(commit: Commit) -> str:
    return _FULL_LOG.format(
        commit.commit_id,
        commit.committer.name,
        datetime.fromtimestamp(commit.committer.date).strftime("%a %b %d %H:%M:%S %y"),
        commit.message,
    )


def _add_graph(func: Callable[[Commit], str]) -> Callable[[Commit], str]:
    def wrapper(commit: Commit) -> str:
        log = func(commit)
        split_lines = log.splitlines()
        details = "".join(map(lambda item: f"| {item}\n", split_lines[1:]))
        return f"* {split_lines[0]}\n{details}"

    return wrapper
