#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Class CommitStatus."""


from typing import Any, Dict, Optional

from ..exception import CommitStatusError


class CommitStatus:
    """This class defines the basic concept of the commit status.

    Arguments:
        draft_number: The draft number (if the status is draft).
        commit_id: The commit ID (if the status is commit).

    """

    def __init__(
        self,
        *,
        draft_number: Optional[int] = None,
        commit_id: Optional[str] = None,
    ) -> None:

        self._draft_number = draft_number
        self._commit_id = commit_id

    @property
    def is_draft(self) -> bool:
        """Return whether the status is draft, True for draft, False for commit.

        Returns:
            whether the status is draft, True for draft, False for commit.

        """
        return bool(self._draft_number)

    @property
    def draft_number(self) -> Optional[int]:
        """Return the draft number.

        Returns:
            The draft number.

        """
        return self._draft_number

    @property
    def commit_id(self) -> Optional[str]:
        """Return the commit ID.

        Returns:
            The commit ID.

        """
        return self._commit_id

    def get_status_info(self) -> Dict[str, Any]:
        """Get the dict containing the draft number or commit ID.

        Returns:
            A dict containing the draft number or commit ID.

        """
        if self.is_draft:
            return {"draftNumber": self._draft_number}
        return {"commit": self._commit_id}

    def check_authority_for_commit(self) -> None:
        """Check whether the status is a legal commit.

        Raises:
            CommitStatusError: When the status is not a legal commit.

        """
        if self._draft_number is not None:
            raise CommitStatusError(self.is_draft)

    def check_authority_for_draft(self) -> None:
        """Check whether the status is a legal draft.

        Raises:
            CommitStatusError: When the status is not a legal draft.

        """
        if self._draft_number is None or self._commit_id is not None:
            raise CommitStatusError(self.is_draft)

    def checkout(self, commit_id: Optional[str] = None, draft_number: Optional[int] = None) -> None:
        """Checkout to commit or draft.

        Arguments:
            commit_id: The commit ID.
            draft_number: The draft number.

        """
        self._draft_number = draft_number
        self._commit_id = commit_id
