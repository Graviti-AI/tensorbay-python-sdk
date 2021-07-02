#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas log."""
import bisect
from collections import defaultdict
from datetime import datetime
from itertools import islice
from textwrap import indent
from typing import Callable, DefaultDict, Dict, Iterable, Iterator, List, Optional

import click

from ..client.gas import DatasetClientType
from ..client.lazy import PagingList
from ..client.struct import Commit
from .auth import INDENT
from .tbrn import TBRN, TBRNType
from .utility import error, get_gas, shorten

_FULL_LOG = """commit {}
Author: {}
Date: {}

    {}
"""


class LogCommits:  # pylint: disable=too-few-public-methods
    """This class defines the structure of logging commits.

    Arguments:
        all_commits: All the commits from branches that need to be logged.

    """

    def __init__(self, all_commits: Iterable[PagingList[Commit]]):
        # Sort commits from different branches by the date of the latest commit of each branch.
        self._sorted_commits: List[PagingList[Commit]] = sorted(
            all_commits, key=lambda x: x[0].committer.date
        )
        self._keys = [commits[0].committer.date for commits in self._sorted_commits]

    def _merge(self, latest_commit: Commit) -> bool:
        if len(self._sorted_commits) <= 1:
            return False

        date = latest_commit.committer.date
        commit_id = latest_commit.commit_id
        for commits in islice(reversed(self._sorted_commits), 1, None):
            commit = commits[0]
            # Traverse all the commits with the same timestamp,
            # if the commit id is the same as the latest commit,
            # then merge the branch where the latest commit is located.
            if commit.committer.date != date:
                return False
            # Same commit, merge branches.
            if commit.commit_id == commit_id:
                break
        else:
            return False
        # Merge branches.
        del self._sorted_commits[-1]
        del self._keys[-1]
        return True

    def _sort(self) -> None:
        """Sort commits paging list by commit date."""
        # Only one branch exists.
        if len(self._sorted_commits) == 1:
            return

        # Binary insert.
        commits = self._sorted_commits.pop()
        del self._keys[-1]
        date = commits[0].committer.date
        index = bisect.bisect_left(self._keys, date)
        self._sorted_commits.insert(index, commits)
        self._keys.insert(index, date)

    def generate_commits(self) -> Iterator[Commit]:
        """Get the latest commit in commit list.

        Yields:
            The latest commit.

        """
        while True:
            try:
                latest_commit = self._sorted_commits[-1].pop(0)
            except IndexError:
                return
            if self._merge(latest_commit):
                continue
            yield latest_commit
            self._sort()


def _log_all_commits(
    dataset_client: DatasetClientType,
    commit_id_to_branches: DefaultDict[str, List[str]],
    revisions: List[Optional[str]],
    printer: Callable[[Commit, Optional[str]], str],
) -> Iterator[str]:
    all_commits: List[PagingList[Commit]] = [
        dataset_client.list_commits(revision) for revision in revisions
    ]
    if len(all_commits[0]) == 0:
        error(f'Dataset "{dataset_client.name}" has no commit history')

    logging_commits = LogCommits(all_commits=all_commits)
    for commit in logging_commits.generate_commits():
        commit_id = commit.commit_id
        print_branch_name = ", ".join(commit_id_to_branches.get(commit_id, ()))
        yield printer(commit, print_branch_name)


def _implement_log(
    obj: Dict[str, str],
    tbrn: str,
    max_count: Optional[int],
    oneline: bool,
    is_all: bool,
) -> None:
    gas = get_gas(**obj)
    info = TBRN(tbrn=tbrn)
    if info.type != TBRNType.DATASET:
        error(f'To log commits, "{info}" must be a dataset')

    dataset_client = gas._get_dataset_with_any_type(  # pylint: disable=protected-access
        info.dataset_name
    )
    commit_id_to_branches: DefaultDict[str, List[str]] = defaultdict(list)
    for branch in dataset_client.list_branches():
        commit_id_to_branches[branch.commit_id].append(branch.name)
    if is_all:
        revisions: List[Optional[str]] = [branch.name for branch in dataset_client.list_branches()]
    else:
        revisions = [info.revision] if info.revision else [dataset_client.status.branch_name]
    template = _get_oneline_log if oneline else _get_full_log
    log_commits = _log_all_commits(dataset_client, commit_id_to_branches, revisions, template)
    click.echo_via_pager(islice(log_commits, max_count))


def _get_oneline_log(commit: Commit, branch_name: Optional[str]) -> str:
    commit_id = shorten(commit.commit_id)
    if branch_name:
        commit_id = f"{commit_id}({branch_name})"
    return f"{commit_id} {commit.title}\n"


def _get_full_log(commit: Commit, branch_name: Optional[str]) -> str:
    description = commit.description
    if description:
        description = f"\n\n{indent(description, INDENT)}"
    commit_message = f"{commit.title}{description}\n"
    commit_id = commit.commit_id
    if branch_name:
        commit_id = f"{commit_id}({branch_name})"
    return _FULL_LOG.format(
        commit_id,
        commit.committer.name,
        datetime.fromtimestamp(commit.committer.date).strftime("%a %b %d %H:%M:%S %y"),
        commit_message,
    )
