#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas log."""

import bisect
import sys
from collections import defaultdict
from datetime import datetime
from functools import partial
from itertools import cycle, islice, zip_longest
from textwrap import indent
from typing import (
    Callable,
    DefaultDict,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

import click

from tensorbay.cli.auth import INDENT
from tensorbay.cli.tbrn import TBRN, TBRNType
from tensorbay.cli.utility import ContextInfo, error, exception_handler, shorten
from tensorbay.client.gas import DatasetClientType
from tensorbay.client.struct import ROOT_COMMIT_ID, Commit, Draft

_LEFT_BRACKET = click.style("(", fg="yellow", reset=False)
_COMMA = click.style(", ", fg="yellow", reset=False)
_RIGHT_BRACKET = click.style(")", fg="yellow", reset=True)

_FULL_COMMIT_MESSAGE = f"""{click.style("commit {}", fg="yellow")}
Author: {{}}
Date: {{}}

    {{}}
"""

_FULL_DRAFT_MESSAGE = f"""{click.style("draft {}", fg="red")}
Date: {{}}

    {{}}
"""

_ONELINE_COMMIT_MESSAGE = f"""{click.style("{}", fg="yellow")} {{}}
"""

_ONELINE_DRAFT_MESSAGE = f"""{click.style("{}", fg="red")} {{}}
"""

_LOG_COLORS = (
    "red",
    "green",
    "blue",
    "magenta",
    "cyan",
    "bright_blue",
    "bright_magenta",
    "bright_cyan",
    "bright_red",
    "bright_green",
    "bright_yellow",
)
_R = TypeVar("_R", bound="_RootCommitNode")
_D = TypeVar("_D", bound="_DraftNode")
_T = Union["_RootCommitNode", "_DraftNode"]


@exception_handler
def _implement_log(  # pylint: disable=too-many-arguments
    obj: ContextInfo,
    tbrn: str,
    max_count: Optional[int],
    oneline: bool,
    is_all: bool,
    graph: bool,
    show_drafts: bool,
) -> None:
    gas = obj.get_gas()
    tbrn_info = TBRN(tbrn=tbrn)
    if tbrn_info.type != TBRNType.DATASET:
        error(f'To log commits, "{tbrn}" must be a dataset')

    dataset_client = gas._get_dataset_with_any_type(  # pylint: disable=protected-access
        tbrn_info.dataset_name
    )
    commit_id_to_branches: DefaultDict[str, List[str]] = defaultdict(list)
    for branch in dataset_client.list_branches():
        commit_id_to_branches[branch.commit_id].append(branch.name)
    if is_all:
        revisions: List[Optional[str]] = [branch.name for branch in dataset_client.list_branches()]
    else:
        revisions = (
            [tbrn_info.revision] if tbrn_info.revision else [dataset_client.status.branch_name]
        )
    Printer: Union[Type[_GraphPrinter], Type[_Printer]] = _GraphPrinter if graph else _Printer
    message_generator = islice(
        Printer(
            dataset_client, revisions, commit_id_to_branches, oneline, show_drafts=show_drafts
        ).generate_commits_and_drafts_messages(),
        max_count,
    )
    _echo_messages(message_generator)


def _join_branch_names(commit_id: str, branch_names: List[str]) -> str:
    return (
        f"{commit_id} {_LEFT_BRACKET}"
        f"{_COMMA.join(click.style(name, fg='green', reset=False) for name in branch_names)}"
        f"{_RIGHT_BRACKET}"
    )


def _get_oneline_commit_message(commit: Commit, branch_names: Optional[List[str]]) -> str:
    commit_id = shorten(commit.commit_id)
    if branch_names:
        commit_id = _join_branch_names(commit_id, branch_names)
    return _ONELINE_COMMIT_MESSAGE.format(commit_id, commit.title)


def _get_oneline_draft_message(draft: Draft) -> str:
    return _ONELINE_DRAFT_MESSAGE.format(draft.number, draft.title)


def _get_full_commit_message(commit: Commit, branch_names: Optional[List[str]]) -> str:
    description = commit.description
    if description:
        description = f"\n\n{indent(description, INDENT)}"
    commit_message = f"{commit.title}{description}\n"
    commit_id = commit.commit_id
    if branch_names:
        commit_id = _join_branch_names(commit_id, branch_names)
    return _FULL_COMMIT_MESSAGE.format(
        commit_id,
        commit.committer.name,
        datetime.fromtimestamp(commit.committer.date).strftime("%a %b %d %H:%M:%S %y"),
        commit_message,
    )


def _get_full_draft_message(draft: Draft) -> str:
    description = draft.description
    if description:
        description = f"\n\n{indent(description, INDENT)}"
    draft_message = f"{draft.title}{description}\n"
    return _FULL_DRAFT_MESSAGE.format(
        draft.number,
        datetime.fromtimestamp(draft.updated_at).strftime("%a %b %d %H:%M:%S %y"),
        draft_message,
    )


class _Printer:
    """This class defines the structure of logging commits and open drafts.

    Arguments:
        dataset_client: The dataset that needs to be logged.
        revisions: The revisions that needs to be logged.
        oneline: Whether to log with oneline method.
        commit_id_to_branches: The map of commit id to branch name.
        show_drafts: Whether to log open drafts.

    """

    def __init__(
        self,
        dataset_client: DatasetClientType,
        revisions: List[Optional[str]],
        commit_id_to_branches: Dict[str, List[str]],
        oneline: bool,
        *,
        show_drafts: bool,
    ):
        all_commit_logs = list(map(dataset_client.list_commits, revisions))
        all_drafts: List[Draft] = []
        error_message = f'Dataset "{dataset_client.name}" has no commit history'
        if show_drafts:
            error_message += " or open drafts"
            for revision in revisions:
                all_drafts.extend(dataset_client.list_drafts(branch_name=revision))

        if not all_commit_logs[0]:
            if not all_drafts:
                error(error_message)
            self._sorted_commit_logs = []
        else:
            # Sort logs from different branches by the date of the latest commit of each branch.
            self._sorted_commit_logs = sorted(all_commit_logs, key=lambda x: x[0].committer.date)

        self._commit_id_to_branches = commit_id_to_branches
        self._commit_printer, self._draft_printer = (
            (_get_oneline_commit_message, _get_oneline_draft_message)
            if oneline
            else (_get_full_commit_message, _get_full_draft_message)
        )

        self._sorted_drafts = sorted(all_drafts, key=lambda x: x.updated_at)
        self._keys = [log[0].committer.date for log in self._sorted_commit_logs]

    def _merge(self, latest_commit: Commit) -> bool:
        if len(self._sorted_commit_logs) <= 1:
            return False

        date = latest_commit.committer.date
        commit_id = latest_commit.commit_id
        for log in islice(reversed(self._sorted_commit_logs), 1, None):
            commit = log[0]
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
        del self._sorted_commit_logs[-1]
        del self._keys[-1]
        return True

    def _sort(self) -> None:
        """Sort commits paging list by commit date."""
        # Only one branch exists.
        if len(self._sorted_commit_logs) == 1:
            return

        # Binary insert.
        log = self._sorted_commit_logs.pop()
        del self._keys[-1]
        date = log[0].committer.date
        index = bisect.bisect_left(self._keys, date)
        self._sorted_commit_logs.insert(index, log)
        self._keys.insert(index, date)

    def generate_commits_and_drafts_messages(self) -> Iterator[str]:
        """Get the messages of all commits and open drafts.

        Yields:
            The commit or draft message.

        """
        latest_draft: Optional[Draft] = None
        while True:
            try:
                latest_commit = self._sorted_commit_logs[-1][0]
            except IndexError:
                if latest_draft:
                    yield self._draft_printer(latest_draft)
                if self._sorted_drafts:
                    yield from map(self._draft_printer, reversed(self._sorted_drafts))
                return
            if not latest_draft and self._sorted_drafts:
                latest_draft = self._sorted_drafts.pop()
            if latest_draft and latest_draft.updated_at > latest_commit.committer.date:
                yield self._draft_printer(latest_draft)
                latest_draft = None
            else:
                del self._sorted_commit_logs[-1][0]
                if self._merge(latest_commit):
                    continue
                yield self._commit_printer(
                    latest_commit, self._commit_id_to_branches.get(latest_commit.commit_id)
                )
                self._sort()


class _RootCommitNode:  # pylint: disable=too-many-instance-attributes
    SIGN = "*"

    def __init__(self) -> None:
        self.parent: Optional[_RootCommitNode] = None
        self.date = 0
        self.key = ROOT_COMMIT_ID
        self.available_child_num = 0
        self.get_oneline_message: Callable[
            [List[str]], str
        ] = lambda _: _ONELINE_COMMIT_MESSAGE.format(shorten(ROOT_COMMIT_ID), "ROOT_COMMIT")
        self.get_full_message: Callable[
            [List[str]], str
        ] = lambda _: f'{click.style("ROOT_COMMIT {}", fg="yellow")}'.format(self.key)

    def add_child(self, child_node: _T) -> None:
        """Save the child node for the parent node.

        Arguments:
            child_node: The child node.

        """
        child_node.parent = self
        self.available_child_num += 1


class _CommitNode(_RootCommitNode):
    """This class defines the tree struct of graphical logging commits.

    Arguments:
        commit: The commit that needs to be saved in the tree.

    """

    def __init__(self, commit: Commit):
        super().__init__()
        self.commit = commit
        self.date = commit.committer.date
        self.key = commit.commit_id
        self.get_oneline_message = partial(_get_oneline_commit_message, commit)
        self.get_full_message = partial(_get_full_commit_message, commit)


class _DraftNode:  # pylint: disable=too-many-instance-attributes
    """This class defines the tree struct of graphical logging drafts.

    Arguments:
        draft: The draft that needs to be saved in the tree.

    """

    SIGN = "#"

    def __init__(self, draft: Draft) -> None:
        self.draft = draft
        self.parent: Optional[_CommitNode] = None
        self.date = draft.updated_at
        self.available_child_num = 0
        self.key = str(draft.number)
        self.get_oneline_message: Callable[[List[str]], str] = lambda _: _get_oneline_draft_message(
            draft
        )
        self.get_full_message: Callable[[List[str]], str] = lambda _: _get_full_draft_message(draft)


class _GraphPrinter:
    """This class defines the structure of logging graphical commits and open drafts stack.

    Arguments:
        dataset_client: The dataset that needs to be logged.
        revisions: The revisions that needs to be logged.
        oneline: Whether to log with oneline method.
        commit_id_to_branches: The map of commit id to branch name.
        show_drafts: Whether to log open drafts.

    """

    def __init__(
        self,
        dataset_client: DatasetClientType,
        revisions: List[Optional[str]],
        commit_id_to_branches: Dict[str, List[str]],
        oneline: bool,
        *,
        show_drafts: bool,
    ):
        self._key_to_branches = commit_id_to_branches
        self._graph_printer = self._add_oneline_graph if oneline else self._add_full_graph

        self._sorted_leaves = self._build_tree(dataset_client, revisions, show_drafts)
        error_message = f'Dataset "{dataset_client.name}" has no commit history'
        if show_drafts:
            error_message += " or open drafts"
        if not self._sorted_leaves:
            error(error_message)
        self._pointer = 0
        self._merge_pointer: Optional[int] = None
        self._log_colors = cycle(_LOG_COLORS)
        self._layer_colors: List[str] = [next(self._log_colors)]

    def _get_log_node(self) -> _T:
        """Get the next log node.

        Returns:
            The next log node.

        Raises:
            RuntimeError: Graphical logging algorithm error.

        """
        self._merge_pointer = None
        for log_node in islice(self._sorted_leaves, self._pointer, None):
            if log_node.available_child_num == 0:
                return log_node

            self._pointer += 1
            if self._pointer >= len(self._layer_colors):
                self._layer_colors.append(next(self._log_colors))

        raise RuntimeError("Graphical logging algorithm error.")

    def _merge_branches(self, parent: _RootCommitNode) -> None:
        """Merge branches.

        Arguments:
            parent: The parent node.

        """
        index = self._sorted_leaves.index(parent)
        self._pointer, self._merge_pointer = sorted((index, self._pointer))
        del self._sorted_leaves[self._merge_pointer]

    def _set_next_node(self, node: _RootCommitNode) -> None:
        """Set the next node at the position of the printing pointer.

        Arguments:
            node: The next node of the printing pointer.

        """
        node.available_child_num -= 1
        self._sorted_leaves[self._pointer] = node

    def _add_oneline_graph(self, node: _T, original_pointer: int) -> str:
        message = node.get_oneline_message(self._key_to_branches[node.key])
        prefixes = self._get_colorful_prefixes()
        # Don't merge branches.
        if self._merge_pointer is None:
            return f"{self._get_title_prefix(prefixes, original_pointer, node.SIGN)}{message}"

        # Merge branches.
        del self._layer_colors[self._merge_pointer]
        lines = [f"{self._get_title_prefix(prefixes, original_pointer, node.SIGN)}{message}"]
        lines.extend(
            f"{prefixes}\n"
            for prefixes in self._get_merge_prefixes(
                self._get_colorful_prefixes(), self._merge_pointer, self._pointer
            )
        )
        return "".join(lines)

    def _add_full_graph(self, node: _T, original_pointer: int) -> str:
        message = node.get_full_message(self._key_to_branches[node.key])
        splitlines = iter(message.splitlines())
        original_prefixes = self._get_colorful_prefixes()
        lines = [
            f"{self._get_title_prefix(original_prefixes, original_pointer, node.SIGN)}"
            f"{next(splitlines)}\n"
        ]
        # Don't merge branches.
        if self._merge_pointer is None:
            details_prefix = "".join(original_prefixes)
            lines.extend(f"{details_prefix}{line}\n" for line in splitlines)
        else:
            # Merge branches.
            del self._layer_colors[self._merge_pointer]
            prefixes = self._get_colorful_prefixes()
            merge_prefixes = self._get_merge_prefixes(prefixes, self._merge_pointer, self._pointer)
            lines.extend(self._combine_details(list(merge_prefixes), list(splitlines), prefixes))
        return "".join(lines)

    def _get_merge_prefixes(
        self, prefixes: List[str], merge_pointer: int, pointer: int
    ) -> Iterator[str]:
        for i in range(merge_pointer, pointer, -1):
            temp_prefixes = prefixes.copy()
            temp_prefixes[2 * i - 1] = click.style("/", fg=self._layer_colors[pointer])
            if i == merge_pointer:
                for j, color in enumerate(self._layer_colors[i:], i):
                    temp_prefixes[2 * j] = " "
                    temp_prefixes[2 * j + 1] = click.style("/", fg=color)
            yield "".join(temp_prefixes)

    def _get_colorful_prefixes(self) -> List[str]:
        prefixes = []
        for color in self._layer_colors:
            prefixes.append(click.style("|", fg=color))
            prefixes.append(" ")
        return prefixes

    @staticmethod
    def _get_title_prefix(prefixes: List[str], original_pointer: int, sign: str) -> str:
        title_prefixes = prefixes.copy()
        title_prefixes[2 * original_pointer] = sign
        return "".join(title_prefixes)

    @staticmethod
    def _combine_details(
        merge_prefixes: List[str], messages: List[str], fill_prefix: List[str]
    ) -> Iterator[str]:
        fillvalue = "" if len(merge_prefixes) > len(messages) else "".join(fill_prefix)
        for prefix, message in zip_longest(merge_prefixes, messages, fillvalue=fillvalue):
            yield f"{prefix}  {message}\n"

    def _build_tree(
        self,
        dataset_client: DatasetClientType,
        revisions: List[Optional[str]],
        show_drafts: bool,
    ) -> List[_T]:
        commit_to_node: Dict[str, _RootCommitNode] = {}
        leaves: Dict[str, _T] = {}
        for revision in revisions:
            child_node: Optional[_RootCommitNode] = None
            for commit in dataset_client.list_commits(revision):
                commit_id = commit.commit_id
                current_node = commit_to_node.get(commit_id, _CommitNode(commit))
                if child_node:
                    current_node.add_child(child_node)
                # Commit already exists in the tree.
                if commit_id in commit_to_node:
                    break

                # Save leaf node to leaf set.
                if not child_node:
                    leaves[commit_id] = current_node
                # Save commit to commit dict.
                commit_to_node[commit_id] = current_node
                child_node = current_node
            if show_drafts:
                for draft in dataset_client.list_drafts(branch_name=revision):
                    draft_node = _DraftNode(draft)
                    leaves[draft_node.key] = draft_node
                    self._key_to_branches[draft_node.key] = [draft.branch_name]
                    parent_commit_id = draft.parent_commit_id
                    if parent_commit_id in commit_to_node:
                        parent_node = commit_to_node[parent_commit_id]
                    else:
                        parent_node = _RootCommitNode()
                        commit_to_node[parent_commit_id] = parent_node
                        if child_node:
                            parent_node.add_child(child_node)
                    parent_node.add_child(draft_node)

        return self._check_and_sort_leaves(leaves)

    @staticmethod
    def _check_and_sort_leaves(leaves: Dict[str, _T]) -> List[_T]:
        # Check the correction of leaf set.
        delete_keys = [
            key for key, leaf_node in leaves.items() if leaf_node.available_child_num != 0
        ]
        for key in delete_keys:
            del leaves[key]
        return sorted(leaves.values(), key=lambda x: x.date, reverse=True)

    def generate_commits_and_drafts_messages(self) -> Iterator[str]:
        """Get the graphical message.

        Yields:
            The graphical message.

        """
        change_color = False
        while True:
            current_node = self._get_log_node()
            parent = current_node.parent
            original_pointer = self._pointer
            if parent not in self._sorted_leaves:
                if change_color:
                    # pylint: disable=stop-iteration-return
                    self._layer_colors[self._pointer] = next(self._log_colors)
                    change_color = False
            else:
                # Merge branch.
                change_color = True
                self._merge_branches(parent)
            yield self._graph_printer(
                current_node,
                original_pointer,
            )

            if not parent:
                break
            self._set_next_node(parent)


def _echo_messages(message_generator: Iterable[str]) -> None:
    if sys.platform.startswith("win"):
        for item in message_generator:
            click.echo(item)
    else:
        click.echo_via_pager(message_generator)
