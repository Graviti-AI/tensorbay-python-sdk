#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas log."""
import bisect
from collections import defaultdict
from datetime import datetime
from itertools import islice, zip_longest
from textwrap import indent
from typing import DefaultDict, Dict, Iterator, List, Optional, Type, Union

import click

from ..client.gas import DatasetClientType
from ..client.struct import Commit
from .auth import INDENT
from .tbrn import TBRN, TBRNType
from .utility import error, get_gas, is_win, shorten

_FULL_LOG = """commit {}
Author: {}
Date: {}

    {}
"""


def _implement_log(  # pylint: disable=too-many-arguments
    obj: Dict[str, str],
    tbrn: str,
    max_count: Optional[int],
    oneline: bool,
    is_all: bool,
    graph: bool,
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

    Printer: Union[Type[_GraphPrinter], Type[_CommitPrinter]] = (
        _GraphPrinter if graph else _CommitPrinter
    )
    commit_generator = islice(
        Printer(dataset_client, revisions, commit_id_to_branches, oneline).generate_commits(),
        max_count,
    )
    if is_win():
        for item in commit_generator:
            click.echo(item)
    else:
        click.echo_via_pager(commit_generator)


def _get_oneline_log(commit: Commit, branch_name: Optional[str]) -> str:
    commit_id = shorten(commit.commit_id)
    if branch_name:
        commit_id = f"{commit_id} ({branch_name})"
    return f"{commit_id} {commit.title}\n"


def _get_full_log(commit: Commit, branch_name: Optional[str]) -> str:
    description = commit.description
    if description:
        description = f"\n\n{indent(description, INDENT)}"
    commit_message = f"{commit.title}{description}\n"
    commit_id = commit.commit_id
    if branch_name:
        commit_id = f"{commit_id} ({branch_name})"
    return _FULL_LOG.format(
        commit_id,
        commit.committer.name,
        datetime.fromtimestamp(commit.committer.date).strftime("%a %b %d %H:%M:%S %y"),
        commit_message,
    )


class _CommitPrinter:
    """This class defines the structure of logging commits.

    Arguments:
        dataset_client: The dataset that needs to be logged.
        revisions: The revisions that needs to be logged.
        oneline: Whether to log with oneline method.
        commit_id_to_branches: The map of commit id to branch name.

    """

    def __init__(
        self,
        dataset_client: DatasetClientType,
        revisions: List[Optional[str]],
        commit_id_to_branches: Dict[str, List[str]],
        oneline: bool,
    ):
        all_commits = list(map(dataset_client.list_commits, revisions))

        if len(all_commits[0]) == 0:
            error(f'Dataset "{dataset_client.name}" has no commit history')

        self._commit_id_to_branches = commit_id_to_branches
        self._printer = _get_oneline_log if oneline else _get_full_log

        # Sort commits from different branches by the date of the latest commit of each branch.
        self._sorted_commits = sorted(all_commits, key=lambda x: x[0].committer.date)
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

    def _generate_commits(self) -> Iterator[Commit]:
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

    def generate_commits(self) -> Iterator[str]:
        """Get the the log of all commits.

        Yields:
            The commit log.

        """
        for commit in self._generate_commits():
            commit_id = commit.commit_id
            print_branch_name = ", ".join(self._commit_id_to_branches.get(commit_id, ()))
            yield self._printer(commit, print_branch_name)


class _CommitNode:
    """This class defines the tree struct of graphical logging commits.

    Arguments:
        commit: The commit that needs to be saved in the tree.

    """

    def __init__(self, commit: Commit):
        self.commit = commit
        self.children: List[_CommitNode] = []
        self.available_child_num = 0
        self.parent: Optional[_CommitNode] = None

    def add_child(self, child_node: "_CommitNode") -> None:
        """Save the child node for the parent node.

        Arguments:
            child_node: The child node.

        """
        child_node.parent = self
        self.children.append(child_node)
        self.available_child_num += 1


class _GraphPrinter:
    """This class defines the structure of logging graphical commits stack.

    Arguments:
        dataset_client: The dataset that needs to be logged.
        revisions: The revisions that needs to be logged.
        oneline: Whether to log with oneline method.
        commit_id_to_branches: The map of commit id to branch name.

    """

    def __init__(
        self,
        dataset_client: DatasetClientType,
        revisions: List[Optional[str]],
        commit_id_to_branches: Dict[str, List[str]],
        oneline: bool,
    ):
        self._commit_id_to_branches = commit_id_to_branches
        self._graph_printer = self._add_graph_oneline if oneline else self._add_graph_full

        self._sorted_leaves = self._build_commit_tree(dataset_client, revisions)
        self._layer = 1
        self._pointer = 0
        self._merge_pointer: Optional[int] = None

    def _get_log_node(self) -> _CommitNode:
        """Get the next log commit node.

        Returns:
            The next log commit node.

        Raises:
            RuntimeError: Graphical logging algorithm error.

        """
        self._merge_pointer = None
        for log_node in islice(self._sorted_leaves, self._pointer, None):
            if log_node.available_child_num == 0:
                return log_node

            self._pointer += 1
            if self._pointer >= self._layer:
                self._layer += 1

        raise RuntimeError("Graphical logging algorithm error.")

    def _merge_branches(self, parent: Optional[_CommitNode]) -> int:
        """Merge branches.

        Arguments:
            parent: The parent node.

        Returns:
            The original print pointer.

        """
        if parent not in self._sorted_leaves:
            return self._pointer
        index = self._sorted_leaves.index(parent)
        original_pointer = self._pointer
        self._pointer, self._merge_pointer = sorted((index, self._pointer))
        self._layer -= 1
        del self._sorted_leaves[self._merge_pointer]
        return original_pointer

    def _set_next_node(self, node: _CommitNode) -> None:
        """Set the next node at the position of the printing pointer.

        Arguments:
            node: The next node of the printing pointer.

        """
        node.available_child_num -= 1
        self._sorted_leaves[self._pointer] = node

    def _add_graph_oneline(
        self, commit: Commit, branch_name: Optional[str], original_pointer: int
    ) -> str:
        log = _get_oneline_log(commit, branch_name)
        prefixes = ["|"] * self._layer
        # Don't merge branches.
        if self._merge_pointer is None:
            return f"{self._get_title_prefix(prefixes, original_pointer)} {log}"

        # Merge branches.
        prefixes.append("|")
        lines = [f"{self._get_title_prefix(prefixes, original_pointer)} {log}"]
        lines.extend(f"{prefixes}\n" for prefixes in self._get_merge_prefixes())
        return "".join(lines)

    def _add_graph_full(
        self, commit: Commit, branch_name: Optional[str], original_pointer: int
    ) -> str:
        log = _get_full_log(commit, branch_name)
        splitlines = iter(log.splitlines())
        prefixes = ["|"] * self._layer
        # Don't merge branches.
        if self._merge_pointer is None:
            details_prefix = " ".join(prefixes)
            lines = [f"{self._get_title_prefix(prefixes, original_pointer)} {next(splitlines)}\n"]
            lines.extend(f"{details_prefix} {line}\n" for line in splitlines)
        else:
            # Merge branches.
            prefixes.append("|")
            merge_prefixes = self._get_merge_prefixes()
            lines = [f"{self._get_title_prefix(prefixes, original_pointer)} {next(splitlines)}\n"]
            lines.extend(self._combine_details(list(merge_prefixes), list(splitlines)))

        return "".join(lines)

    def _get_merge_prefixes(self) -> Iterator[str]:
        for i in range(self._merge_pointer, self._pointer, -1):  # type: ignore[arg-type]
            prefixes = ["| "] * self._layer
            prefixes[i - 1] = "|/"
            yield "".join(prefixes)

    @staticmethod
    def _get_title_prefix(prefixes: List[str], original_pointer: int) -> str:
        title_prefixes = prefixes.copy()
        title_prefixes[original_pointer] = "*"
        return " ".join(title_prefixes)

    @staticmethod
    def _combine_details(merge_prefixes: List[str], messages: List[str]) -> Iterator[str]:
        fillvalue = (
            "" if len(merge_prefixes) > len(messages) else merge_prefixes[0].replace("/", " ")
        )
        for prefix, message in zip_longest(merge_prefixes, messages, fillvalue=fillvalue):
            yield f"{prefix}  {message}\n"

    @staticmethod
    def _build_commit_tree(
        dataset_client: DatasetClientType, revisions: List[Optional[str]]
    ) -> List[_CommitNode]:
        commit_to_node: Dict[str, _CommitNode] = {}
        leaves: Dict[str, _CommitNode] = {}
        for revision in revisions:
            commits = dataset_client.list_commits(revision)
            child_node: Optional[_CommitNode] = None
            for index, commit in enumerate(commits):
                commit_id = commit.commit_id
                current_node = commit_to_node.get(commit_id, _CommitNode(commit))
                if child_node:
                    current_node.add_child(child_node)
                # Commit already exists in the tree.
                if commit_id in commit_to_node:
                    break

                # Save leaf node to leaf set.
                if index == 0:
                    leaves[commit_id] = current_node
                # Save commit to commit dict.
                commit_to_node[commit_id] = current_node
                child_node = current_node

        # Check the correction of leaf set.
        for commit_id in tuple(leaves):
            if leaves[commit_id].available_child_num != 0:
                del leaves[commit_id]
        return sorted(leaves.values(), key=lambda x: x.commit.committer.date, reverse=True)

    def generate_commits(self) -> Iterator[str]:
        """Get the graphical commit log.

        Yields:
            The graphical commit log.

        """
        while True:
            current_node = self._get_log_node()
            parent = current_node.parent
            # Merge branch.
            original_pointer = self._merge_branches(parent)

            print_branch_name = ", ".join(
                self._commit_id_to_branches.get(current_node.commit.commit_id, ())
            )
            yield self._graph_printer(current_node.commit, print_branch_name, original_pointer)

            if not parent:
                break
            self._set_next_node(parent)
