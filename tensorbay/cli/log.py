#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas log."""

from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

import click

from ..client.struct import Commit
from .tbrn import TBRN
from .utility import get_dataset_client, get_gas, shorten

_FULL_LOG = """commit {}
Author: {}
Date: {}

    {}

    {}

"""


def _implement_log(  # pylint: disable=too-many-locals
    obj: Dict[str, str],
    tbrn: str,
    max_count: Optional[int],
    oneline: bool,
    is_all: bool,
) -> None:
    gas = get_gas(**obj)
    info = TBRN(tbrn=tbrn)
    dataset_client = get_dataset_client(gas, info)

    branch_name_to_commits: Dict[str, List[Commit]] = defaultdict(list)
    commit_id_to_branch: Dict[str, Set[str]] = defaultdict(set)
    if is_all:
        branches = dataset_client.list_branches()
        base_branch_name = branches[0].name
        for branch in branches:
            branch_name = branch.name
            for commit in dataset_client.list_commits(branch_name):
                commit_id = commit.commit_id
                commit_id_to_branch[commit_id].add(branch_name)
                if commit_id not in commit_id_to_branch:
                    branch_name_to_commits[branch_name].append(commit)
                else:
                    break
        commits = _create_commits(branch_name_to_commits, base_branch_name, commit_id_to_branch)
        commits = commits[:max_count]
    else:
        base_branch_name = "current"
        for commit in dataset_client.list_commits(info.revision)[:max_count]:
            branch_name_to_commits[base_branch_name].append(commit)
            commit_id_to_branch[commit.commit_id].add(base_branch_name)
        commits = _create_commits(branch_name_to_commits, base_branch_name, commit_id_to_branch)

    template = _get_oneline_log if oneline else _get_full_log
    click.echo_via_pager(template(commit) for commit in commits)


def _create_commits(
    branch_name_to_commits: Dict[str, List[Commit]],
    branch_name: str,
    commit_id_to_branch: Dict[str, Set[str]],
) -> List[Commit]:
    commits = []
    for commit in branch_name_to_commits[branch_name]:
        branch_names = commit_id_to_branch[commit.commit_id]
        if len(branch_names) > 1:
            for split_branch_name in branch_names:
                if split_branch_name != branch_name:
                    commits.extend(
                        _create_commits(
                            branch_name_to_commits, split_branch_name, commit_id_to_branch
                        )
                    )
        else:
            commits.append(commit)

    return commits


def _get_oneline_log(commit: Commit) -> str:
    return f"{shorten(commit.commit_id)} {commit.title}\n"


def _get_full_log(commit: Commit) -> str:
    return _FULL_LOG.format(
        commit.commit_id,
        commit.committer.name,
        datetime.fromtimestamp(commit.committer.date).strftime("%a %b %d %H:%M:%S %y"),
        commit.title,
        commit.description,
    )
